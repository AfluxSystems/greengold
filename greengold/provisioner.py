import logging


log = logging.getLogger()


class Provisioner:
    def __init__(self, provisioner_data):
        self.provisioner_data = provisioner_data
        self.require_provisioner()
        self.script = self.load_provisioner()

    def require_provisioner(self):
        pass

    def load_provisioner(self):
        log.info(f"Loading provisioner")
        return []
