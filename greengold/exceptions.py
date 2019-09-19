

class GreenGoldException(Exception):
    pass


class ConfigException(GreenGoldException):
    pass


class ConfigParseException(ConfigException):
    pass


class ClientException(GreenGoldException):
    pass


class AWSClientException(ClientException):
    pass


class AWSConnectionException(AWSClientException):
    pass


class BuilderException(GreenGoldException):
    pass
