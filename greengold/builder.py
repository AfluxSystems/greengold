import os
import json
import logging
from greengold import exceptions as ggexc
from greengold.launcher import Launcher
from greengold.provisioner import Provisioner
from greengold.clients.aws import AWSClient
from greengold.utils import timestamp


log = logging.getLogger()


class Builder:

    def __init__(self, config):
        self.config = config
        self.required_provisioners = {"sshd"}
        self.aws = AWSClient()

    def build(self):
        launcher = Launcher(self.config)
        instance = launcher.provision(self.provisioners())
        log.info(f"Provisioned instance {instance.id} has been created")
        ami = None
        try:
            log.info(f"Stopping instance {instance.id}...")
            instance.stop()
            instance.wait_until_stopped()
            log.debug(f"Instance {instance.id} has been stopped")

            # Modify ena_support attribute
            instance.modify_attribute(EnaSupport={"Value": True})
            # Create AMI
            ami = self.create_ami(instance)
            # Write AMI to manifest
            manifest_data = {
                "ami_id": ami.id,
                "ami_name": ami.name,
                "tags": self.config.data["tags"],
                # "variables": {},
            }
            manifest_name = f"{self.config.data['ami_name']}_manifest.json"
            if os.path.exists(manifest_name):
                log.debug(f"Found existing {manifest_name}. Removing.")
                os.remove(manifest_name)
            with open(manifest_name, "w") as f:
                log.info(f"Writing AMI manifest to {manifest_name}")
                json.dump(manifest_data, f, indent=4)
        except Exception:
            log.exception(f"Error while building. Rolling back.")
            if ami:
                self.delete_ami(ami)
            raise
        finally:
            log.info(f"Terminating instance {instance.id}")
            instance.terminate()
        return ami

    def provisioners(self):
        script = []
        unique_provisioner_keys = set().union(*(d.keys() for d in self.config.data["provisioners"]))
        missing_provisioners = self.required_provisioners - unique_provisioner_keys
        if missing_provisioners:
            raise ggexc.BuilderException(f"Missing required provisioners {list(missing_provisioners)}")

        for provisioner in self.config.data["provisioners"]:
            script += Provisioner(provisioner).script

        script += [
            "sudo truncate -s 0 /home/ubuntu/.ssh/authorized_keys",
        ]

        return script

    def create_ami(self, instance):
        ec2_client = self.aws.get_client("ec2")
        log.info(f"Creating new AMI from instance {instance.id}")
        ami_id = ec2_client.create_image(
            InstanceId=instance.id,
            Name=f"{self.config.data['ami_name']}-{timestamp()}",
            BlockDeviceMappings=self.config.data["block_device_mappings"]
        )["ImageId"]
        ami = self.aws.get_image(ami_id)
        log.info(f"Waiting for new AMI {ami.id} to become available...")
        ami.wait_until_exists(
            Filters=[
                {
                    'Name': 'state',
                    'Values': [
                        'available',
                        'failed'
                    ]
                }
            ]
        )
        if ami.state == 'failed':
            raise ggexc.AMIManagerException(f"Image {ami.id} failed provision "
                                            f"with reason: {ami.state_reason['Message']}")
        log.info(f"New AMI {ami.id} is now available")
        return ami

    def delete_ami(self, ami):
        ec2_client = self.aws.get_client("ec2")
        snapshots = [s["Ebs"]["SnapshotId"] for s in ami.block_device_mappings if "Ebs" in s]
        log.info(f"Removing AMI {ami.id}")
        ami.deregister()
        for snaphot_id in snapshots:
            log.info(f"Removing Snapshot {snaphot_id}")
            ec2_client.delete_snapshot(
                SnapshotId=snaphot_id
            )
