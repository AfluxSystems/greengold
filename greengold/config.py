import os
import yaml
import json

from greengold.clients.aws import AWSClient
from greengold import exceptions as ppexc


class Config:
    def __init__(self, config_file, cli_options):
        self.config_file = config_file
        self.config_data = self.load_file(self.config_file)
        self.cli_options = cli_options
        self.load_defaults()

    @staticmethod
    def load_file(path: str) -> dict:
        _, file_extension = os.path.splitext(path)
        with open(path, 'r') as f:
            if file_extension in ('.yml', '.yaml'):
                config_data = yaml.full_load(f)
            elif file_extension == '.json':
                config_data = json.load(f)
            else:
                raise ppexc.ConfigParseException(f"Unknown file extension '{file_extension}'")
        # TODO: Validate syntax
        return config_data if config_data else {}

    def load_defaults(self) -> dict:
        platform = self.config_data.get("platform", "ubuntu-18.04")
        # self.config_data["variables"] = self.config_data.get("variables", {})
        self.config_data["files"] = self.config_data.get("files", [])
        self.config_data["tags"] = self.config_data.get("tags", {})
        self.config_data["tags"]["platform"] = self.config_data["tags"].get("platform", platform)
        self.config_data["block_device_mappings"] = self.config_data.get(
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
        self.config_data["network_interfaces"] = self.config_data.get("network_interfaces", [])

        if "ami_id" in self.config_data:
            return

        self.config_data["source_ami"] = self.config_data.get(
            "source_ami",
            AWSClient().source_ami(self.config_data.get("source_ami_name", platform))
        )

    def resolve_top_level_key(self, key, raise_exc=True):
        return self.resolve_key(
            self.config_file.get(key, None),
            self.cli_options.get(key, None),
            default_key=key,
            raise_exc=raise_exc
        )

    def resolve_key(self, config_val, cli_option, default_key: str, raise_exc=True):
        if cli_option is not None:
            result = cli_option
        elif config_val is not None:
            result = config_val
        else:
            result = self.defaults.get(default_key, None)
        if result is None and raise_exc:
            raise ppexc.ConfigException(f"Unable to resolve value")
        return result
