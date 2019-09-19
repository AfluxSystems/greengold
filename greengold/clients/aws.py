import boto3
from greengold import exceptions as ggexc


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
            response = client.describe_images(
                Filters=filters,
                Owners=[self.root_account]
            )
            return sorted(response['Images'],
                          key=lambda i: i['CreationDate'],
                          reverse=True)[0]["ImageId"]
        except IndexError:
            raise ggexc.AWSClientException(
                f"No image found for filters {filters} in account {self.root_account}"
            )
        except Exception as exc:
            raise ggexc.AWSConnectionException(f"An error occurred calling AWS") from exc

    def get_client(self, resource, region=None, **kwargs):
        return boto3.client(resource, region_name=region or self.region, **kwargs)
