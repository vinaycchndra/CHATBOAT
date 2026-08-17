class DomainException(Exception):
    pass

class UserAlreadyExistsException(DomainException):
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"User with email '{email}' already exists.")


class InvalidInputError(DomainException): 
    def __init__(self, message: str): 
        self.message = message 
        super().__init__(message)

class EntityDoesNotExist(DomainException): 
    def __init__(self, message: str): 
        self.message = message 
        super().__init__(message)


class UnAuthorizedAccess(DomainException): 
    def __init__(self, message: str):
        self.message = message 
        super().__init__(message)


class NothingToUpdate(DomainException): 
    def __init__(self, message: str): 
        self.message = message 
        super().__init__(message)