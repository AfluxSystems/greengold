

class GreenGoldException(Exception):
    pass


class ConfigException(GreenGoldException):
    pass


class ConfigParseException(ConfigException):
    pass
