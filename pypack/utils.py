import click


def info(message):
    click.secho(message, fg="green")


def error(message):
    click.secho(message, fg="red", bold=True, err=True)

