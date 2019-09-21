from greengold import exceptions as ggexc


class BaseProvisioner:
    def __init__(self, config, options=None):
        self.config = config
        self.options = self.validate_options(options or {})
        self.modify_config()

    def modify_config(self):
        pass

    def required_keys(self):
        return set()

    def validate_options(self, options):
        if isinstance(options, dict):
            keyset = set([k for k in options.keys()])
            missing_keys = self.required_keys() - keyset
            if missing_keys:
                raise ggexc.ProvisionerException(f"Missing required {self.__class__.__name__} "
                                                 f"provisioner keys {list(missing_keys)}")
        return options

    def get_script(self):
        raise NotImplementedError(f"Provisioner has not implemented required method get_script()")
