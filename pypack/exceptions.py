

class PyPackException(Exception):
    pass


class ConfigException(PyPackException):
    pass


class ConfigParseException(ConfigException):
    pass
