from greengold.clients.aws import AWSClient


class Launcher:
    def __init__(self, config):
        self.config = config
        self.aws = AWSClient()

    def provision(self, script):
        instance = self.launch()

    def launch(self):
        ec2_client = self.aws.get_client("ec2")
        # TODO: Here, launch a new instance
