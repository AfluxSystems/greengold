import base64
import logging
from greengold.clients.aws import AWSClient
from greengold.clients.ssh import SSHClient


log = logging.getLogger("greengold")


class Launcher:
    def __init__(self, config, user_data=None):
        self.config = config
        self.user_data = user_data or []
        self.aws = AWSClient()

    def provision(self, script):
        instance = self.launch()
        try:
            ip_address = instance.public_ip_address
            log.debug(f"Instance {instance.id} has IP address {ip_address}")
            ssh_client = SSHClient(
                ip_address,
                self.config.data["user"],
                self.config.data["ssh_key"]
            )
            log.info(f"Waiting for instance {instance.id} to accept SSH connections...")
            ssh_client.wait_until_ssh_ready()
            log.info(f"Instance {instance.id} is ready for SSH")
            with ssh_client as conn:
                log.info(f"Waiting for instance {instance.id} boot processes to finish...")
                ssh_client.wait_on_command("test -f /var/lib/cloud/instance/boot-finished", conn=conn)
                log.info(f"Instance {instance.id} boot has finished")

                # TODO: SCP config["files"] to host

                log.info(f"Running provisioner scripts on instance {instance.id}")
                for line in script:
                    ssh_client.exec(line, conn=conn, expected_return_code=0)
            return instance
        except Exception:
            log.exception(f"Failed to complete provisioning for instance {instance.id}. Rolling back.")
            instance.terminate()
            raise

    def launch(self):
        log.info(f"Launching new EC2 instance from source AMI {self.config.data['source_ami']}")
        ec2_client = self.aws.get_client("ec2")
        instance_id = ec2_client.run_instances(
            BlockDeviceMappings=self.config.data["block_device_mappings"],
            ImageId=self.config.data["source_ami"],
            MinCount=1,
            MaxCount=1,
            KeyName=self.config.data["key_name"],
            InstanceType=self.config.data["instance_type"],
            NetworkInterfaces=self.config.data["network_interfaces"],
            TagSpecifications=[
                {
                    "ResourceType": "instance",
                    "Tags": self.aws.format_tags(
                        {
                            "Name": f"Greengold Builder {self.config.data['ami_name']}",
                            "owner": self.config.data["tags"]["owner"],
                        }
                    )
                }
            ],
            IamInstanceProfile={"Arn": self.config.data["builder_instance_profile_arn"]},
            UserData=base64.b64encode("\n".join(self.user_data).encode())
        )["Instances"][0]["InstanceId"]
        instance = self.aws.get_instance(instance_id)
        log.info(f"EC2 instance {instance.id} has been created")
        try:
            log.info(f"Waiting for instance {instance.id} to enter running state...")
            instance.wait_until_running()
            log.info(f"Instance {instance.id} is ready")
            return instance
        except Exception:
            log.error(f"Instance {instance.id} failed to enter running state on time. Terminating.")
            instance.terminate()
            raise
