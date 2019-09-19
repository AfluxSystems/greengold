import click
import datetime


# def info(message, module=None):
#     click.secho(format_message(module or "main", message), fg="green")
#
#
# def error(message, module=None):
#     click.secho(format_message(module or "main", message), fg="red", bold=True, err=True)
#
#
# def format_message(module, message):
#     return f"{module}==> {message}"


def iso_timestamp():
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M%S")
