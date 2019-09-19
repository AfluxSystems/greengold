

class GreenGoldException(Exception):
    pass


class ConfigException(GreenGoldException):
    pass


class ConfigParseException(ConfigException):
    pass


class ClientException(GreenGoldException):
    pass


class SSHClientException(ClientException):
    pass


class SSHReturnCodeException(SSHClientException):
    pass


class AWSClientException(ClientException):
    pass


class AWSConnectionException(AWSClientException):
    pass


class BuilderException(GreenGoldException):
    pass


class AMIManagerException(GreenGoldException):
    pass
