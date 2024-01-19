

class DbError(Exception):
    pass

class DbNotFoundError(DbError):
    pass

class DbAlreadyExistsError(DbError):
    pass
