import sys
import logging
import click
from greengold.config import Config
from greengold.builder import Builder

log = logging.getLogger()

logging.getLogger('boto3').setLevel(logging.ERROR)
logging.getLogger('botocore').setLevel(logging.ERROR)
logging.getLogger('paramiko').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)


@click.command()
@click.option("-c", "--config-file", type=click.Path(exists=True, dir_okay=False), required=True)
@click.option("-i", "--ssh-key", type=click.Path(exists=True, dir_okay=False))
@click.option("-p", "--passphrase")
def main(config_file, ssh_key, passphrase):
    log.info(f"Greengold has started")
    cli_options = {
        "ssh_key": ssh_key,
        "passphrase": passphrase,
    }
    # Load config, which handles variable precedence and template variables
    # Example config file:
    # https://github.com/zendesk/foundation_secure_amis/blob/master/packer/ubuntu18.04_ldap_server.yml
    log.info(f"Loading config file {config_file}")
    config = Config(config_file, cli_options)
    log.info(f"Running builder for prospective AMI {config.data['ami_name']}")
    ami = Builder(config).build()
    log.info(f"New AMI {ami.name} ({ami.id}) has been created")


if __name__ == "__main__":
    stream_handler = logging.StreamHandler(sys.stdout)
    log.addHandler(stream_handler)
    log.setLevel(logging.DEBUG)
    main()
