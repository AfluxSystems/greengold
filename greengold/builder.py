import os
from greengold import exceptions as ggexc
from greengold.launcher import Launcher
from greengold.provisioner import Provisioner


class Builder:

    def __init__(self, config):
        self.config = config
        self.required_provisioners = {"sshd"}

    def build(self):
        manifest_name = f"{self.config.data['ami_name']}_manifest.json"

        if os.path.exists(manifest_name):
            os.remove(manifest_name)

        launcher = Launcher(self.config)
        launcher.provision(self.provisioners())
        return 1

    def provisioners(self):
        script = []
        unique_provisioner_keys = set().union(*(d.keys() for d in self.config.data["provisioners"]))
        missing_provisioners = self.required_provisioners - unique_provisioner_keys
        if missing_provisioners:
            raise ggexc.BuilderException(f"Missing required provisioners {list(missing_provisioners)}")

        for provisioner in self.config.data["provisioners"]:
            script += Provisioner(provisioner).script

        script += [
            "sudo truncate -s 0 /home/ubuntu/.ssh/authorized_keys",
        ]

        return script
