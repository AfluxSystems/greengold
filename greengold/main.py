import click
from greengold import utils
from greengold.config import Config


@click.command()
@click.option("-c", "--config-file", type=click.Path(exists=True, dir_okay=False), required=True)
def main(config_file):
    # - Pack all cli options into cli_options
    cli_options = {}

    # Load config, which handles variable precedence and template variables
    # Example config file:
    # https://github.com/zendesk/foundation_secure_amis/blob/master/packer/ubuntu18.04_ldap_server.yml
    config = Config(config_file, cli_options)
    utils.info("Cool")




if __name__ == "__main__":
    main()
