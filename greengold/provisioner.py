import logging
import importlib
from greengold.provisioners.base import BaseProvisioner
from greengold import exceptions as ggexc


log = logging.getLogger("greengold")


class Provisioner:
    def __init__(self, config, provisioner_data):
        self.config = config
        self.provisioner_name = str(list(provisioner_data.keys())[0])
        self.provisioner_data = list(provisioner_data.values())[0]
        self.cls = self.import_provisioner()
        self.script = self.init_provisioner().get_script()

    def import_provisioner(self) -> BaseProvisioner:
        module_path = f"greengold.provisioners.{self.provisioner_name}"
        class_name = self.provisioner_name.capitalize()
        try:
            log.debug(f"Importing provisioner module {module_path}")
            module = importlib.import_module(module_path)
            log.debug(f"Loading class {class_name} from module {module_path}")
            cls = getattr(module, class_name)
            if not issubclass(cls, BaseProvisioner):
                raise ggexc.InvalidProvisionerException(f"Provisioner {cls.__name__} is not a subclass of "
                                                        f"greengold.provisioners.base.BaseProvisioner")
            return cls
        except ModuleNotFoundError as exc:
            message = f"No provisioner module named '{module_path}'"
            log.error(message)
            raise ggexc.ProvisionerNotFoundException(message) from exc
        except AttributeError as exc:
            message = f"No Provisioner '{class_name}' in module {module_path}"
            log.error(message)
            raise ggexc.ProvisionerNotFoundException(message) from exc

    def init_provisioner(self) -> BaseProvisioner:
        log.info(f"Initializing {self.provisioner_name} provisioner with options: {self.provisioner_data}")
        return self.cls(self.config, self.provisioner_data)
