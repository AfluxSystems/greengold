import click
from pypack import utils


@click.command()
@click.option("-c", "--config-file", type=click.Path(exists=True, dir_okay=False), required=True)
def main(config_file):
    utils.error("Hello there")


if __name__ == "__main__":
    main()
