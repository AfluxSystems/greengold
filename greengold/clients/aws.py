import logging
import boto3
from greengold import exceptions as ggexc


log = logging.getLogger("greengold")


class AWSClient:

    def __init__(self, root_account=None, region=None):
        self.root_account = root_account or "003521492892"
        self.region = region or "us-east-1"
        self.supported_ami_names = ("liederbach-base",)

    def source_ami(self, ami_name, platform):
        filters = [{"Name": "tag:approved", "Values": ["true"]}]
        if ami_name in self.supported_ami_names:
            filters += [
                {"Name": "name", "Values": [f"{ami_name}-{platform}-*"]}
            ]
        else:
            raise ggexc.AWSClientException(f"{ami_name} is not supported")
        try:
            client = self.get_client("ec2")
            log.debug(f"Searching for source AMI {ami_name} on account {self.root_account} with filters: {filters}")
            response = client.describe_images(
                Filters=filters,
                Owners=[self.root_account]
            )
            ami_id = sorted(response['Images'],
                            key=lambda i: i['CreationDate'],
                            reverse=True)[0]["ImageId"]
            log.info(f"Discovered source AMI {ami_id}")
            return ami_id
        except IndexError:
            raise ggexc.AWSClientException(
                f"No image found for filters {filters} in account {self.root_account}"
            )
        except Exception as exc:
            raise ggexc.AWSConnectionException(f"An error occurred calling AWS") from exc

    def get_instance(self, instance_id):
        return self.get_resource("ec2").Instance(instance_id)

    def get_image(self, image_id):
        return self.get_resource("ec2").Image(image_id)

    def get_client(self, resource, region=None, **kwargs):
        return boto3.client(resource, region_name=region or self.region, **kwargs)

    def get_resource(self, resource, region=None, **kwargs):
        return boto3.resource(resource, region_name=region or self.region, **kwargs)

    @staticmethod
    def format_tags(tag_dict):
        tags = []
        for key, value in tag_dict.items():
            tags.append(
                {
                    "Key": key,
                    "Value": value
                }
            )
        return tags

    @staticmethod
    def format_device_block_mapping(block_device_mappings):
        result = []
        for block_device in block_device_mappings:
            result.append(
                {
                    "DeviceName": block_device["device_name"],
                    "Ebs": {
                        "DeleteOnTermination": block_device["ebs"]["delete_on_termination"],
                        "VolumeSize": block_device["ebs"]["volume_size"],
                        "VolumeType": block_device["ebs"]["volume_type"],
                        "Encrypted": block_device["ebs"]["encrypted"],
                        # "KmsKeyId": block_device["ebs"]["kms_key_id"],
                    }
                }
            )
        return result

    @staticmethod
    def format_network_interfaces(network_interfaces):
        result = []
        for interface in network_interfaces:
            result.append(
                {
                    "DeviceIndex": interface["device_index"],
                    "Groups": interface["groups"],
                    "SubnetId": interface["subnet_id"],
                }
            )
        return result
