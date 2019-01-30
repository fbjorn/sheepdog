class BaseError(Exception):
    pass


class DatabaseFileDoesNotExist(BaseError):
    pass


class DatabaseIsCorrupted(BaseError):
    pass


class KeyDoesNotExist(BaseError):
    pass


class AlreadyExists(BaseError):
    pass
