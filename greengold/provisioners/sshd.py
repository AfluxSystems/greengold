from greengold.provisioners.base import BaseProvisioner


class Sshd(BaseProvisioner):

    def __init__(self, config, options):
        super().__init__(config, options)

    def get_script(self):
        return []
