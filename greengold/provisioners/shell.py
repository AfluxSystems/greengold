import os
import logging
from greengold.provisioners.base import BaseProvisioner


log = logging.getLogger("greengold")


class Shell(BaseProvisioner):

    def modify_config(self):
        if isinstance(self.options, dict):
            self.config["files"].add(self.options["script"])

    def required_keys(self):
        if isinstance(self.options, dict):
            return {"script", "execute_command"}
        return set()

    def get_script(self):
        if isinstance(self.options, dict):
            return [
                self.options["execute_command"].format(
                    script=f"/tmp/{os.path.basename(self.options['script'])}"
                )
            ]
        return self.options
