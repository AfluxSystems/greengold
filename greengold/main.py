import sys
import logging
import click
from greengold import __version__
from greengold.config import Config
from greengold.builder import Builder
from greengold.logging_config import configure_logging


log = logging.getLogger("greengold")


@click.command()
@click.option("-c", "--config-file", type=click.Path(exists=True, dir_okay=False),
              required=True, help="Path to config file describing new AMI to be built.")
@click.option("-i", "--ssh-key", type=click.Path(exists=True, dir_okay=False),
              help="SSH key to use to connect to build instance. "
                   "This should correspond to the key provisioned on the instance via the `key_name` field.")
@click.option("-p", "--passphrase", help="Optional passphrase to decrypt SSH Key.")
@click.option('-v', '--verbose', count=True, help="Increase logging output.")
@click.option('-z', '--no-artifacts', is_flag=True, default=False,
              help="Wet Run, where artifacts are created, but destroyed afterwards.")
@click.version_option(__version__, prog_name="Greengold AMI Builder")
def main(config_file, ssh_key, passphrase, verbose, no_artifacts):
    configure_logging(verbose)
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
    builder = Builder(config)
    ami = builder.build()
    log.info(f"New AMI {ami.name} ({ami.id}) has been created")

    if no_artifacts:
        log.info(f"Wet run detected, removing AMI {ami.id} and related artifacts")
        builder.delete_ami(ami)


if __name__ == "__main__":
    main()
