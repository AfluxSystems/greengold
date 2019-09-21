from greengold.provisioners.base import BaseProvisioner
from greengold.clients.aws import AWSClient


class Volume(BaseProvisioner):

    def __init__(self, config, options):
        super().__init__(config, options)

    def modify_config(self):
        self.config.data["block_device_mappings"].append(
            AWSClient.format_device_block_mapping(
                [{
                    "device_name": self.options["device"],
                    "ebs": {
                        "delete_on_termination": self.options.get("delete_on_termination", True),
                        "volume_size": self.options.get("size", 8),  # GB
                        "volume_type": self.options.get("volume_type", "gp2"),
                        "encrypted": True,
                    }
                }]
            )[0]
        )

    def required_keys(self):
        return {"device", "label", "mount_point"}

    def get_script(self):
        return [
            "sudo DEBIAN_FRONTEND=noninteractive apt-get -y install xfsprogs",

            f"sudo mkfs.xfs -L {self.options['label']} {self.options['device']}",

            f"[ -d {self.options['mount_point']} ] && sudo mkdir -p /mnt{self.options['mount_point']} "
            f"&& sudo mount {self.options['device']} /mnt{self.options['mount_point']} "
            f"&& cd {self.options['mount_point']} "
            f"&& sudo find . -depth -print | sudo cpio -pamVd /mnt{self.options['mount_point']} "
            f"&& sudo sync && cd / && sudo umount /mnt{self.options['mount_point']} "
            f"|| sudo mkdir -p {self.options['mount_point']}",

            f"sudo mount {self.options['device']} {self.options['mount_point']}",

            f"echo 'LABEL={self.options['label']} {self.options['mount_point']} xfs inode64,noatime 0 0' "
            f"| sudo tee -a /etc/fstab",

            '[ -f /etc/cloud/cloud.cfg.d/999_bootcmd.cfg ] '
            '|| echo "bootcmd:" | sudo tee /etc/cloud/cloud.cfg.d/999_bootcmd.cfg',

            f"grep -q {self.options['mount_point']} /etc/cloud/cloud.cfg.d/999_bootcmd.cfg "
            f"|| echo '  - xfs_growfs {self.options['mount_point']}' "
            f"| sudo tee -a /etc/cloud/cloud.cfg.d/999_bootcmd.cfg"
        ]
