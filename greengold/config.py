import os
import yaml
import json

from greengold.clients.aws import AWSClient
from greengold import exceptions as ggexc


class Config:
    def __init__(self, config_file, cli_options):
        self.config_file = config_file
        self.data = self.load_file(self.config_file)
        self.cli_options = cli_options
        self.load_defaults()

    @staticmethod
    def load_file(path: str) -> dict:
        _, file_extension = os.path.splitext(path)
        with open(path, 'r') as f:
            if file_extension in ('.yml', '.yaml'):
                data = yaml.full_load(f)
            elif file_extension == '.json':
                data = json.load(f)
            else:
                raise ggexc.ConfigParseException(f"Unknown file extension '{file_extension}'")
        # TODO: Validate syntax
        return data if data else {}

    def load_defaults(self):
        platform = self.data.get("platform", "ubuntu-18.04")
        base_name, _ = os.path.splitext(os.path.basename(self.config_file))
        # self.data["variables"] = self.data.get("variables", {})

        self.data["ami_name"] = self.data.get("ami_name", base_name)
        self.data["files"] = self.data.get("files", [])
        self.data["tags"] = self.data.get("tags", {})
        self.data["tags"]["platform"] = self.data["tags"].get("platform", platform)
        self.data["block_device_mappings"] = self.data.get(
            "block_device_mappings",
            [
                {
                    "device_name": "/dev/sda1",
                    "ebs": {
                        "delete_on_termination": True,
                        "volume_size": 8,  # GB
                        "volume_type": "gp2"
                    }
                }
            ]
        )
        self.data["network_interfaces"] = self.data.get("network_interfaces", [])

        # if "ami_id" in self.data:
        #     return

        self.data["source_ami_name"] = self.data.get("source_ami_name", "liederbach-base")
        self.data["source_ami"] = self.data.get(
            "source_ami",
            AWSClient().source_ami(self.data["source_ami_name"], platform)
        )
