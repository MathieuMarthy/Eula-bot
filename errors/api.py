

class ApiError(Exception):
    pass

class ApiKeyError(ApiError):
    pass

class ApiNotFoundError(ApiError):
    pass
