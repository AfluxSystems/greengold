import os
import yaml
import json

from pypack import exceptions as ppexc


class Config:
    def __init__(self, config_file, cli_options):
        self.config_file = config_file
        self.config_data = self.load_file(self.config_file)
        self.cli_options = cli_options
        self.defaults = self.load_defaults()

    @staticmethod
    def load_file(path: str) -> dict:
        _, file_extension = os.path.splitext(path)
        with open(path, 'r') as f:
            if file_extension in ('.yml', '.yaml'):
                config_data = yaml.load(f)
            elif file_extension == '.json':
                config_data = json.load(f)
            else:
                raise ppexc.ConfigParseException(f"Unknown file extension '{file_extension}'")
        # TODO: Validate syntax
        return config_data

    def load_defaults(self) -> dict:
        return {}

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
