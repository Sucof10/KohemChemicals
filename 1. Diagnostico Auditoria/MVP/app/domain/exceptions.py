class DomainException(Exception):
    pass

class EntityNotFoundException(DomainException):
    def __init__(self, entity_name: str, entity_id):
        super().__init__(f"{entity_name} con identificador {entity_id} no fue encontrado.")

class AuthenticationFailedException(DomainException):
    def __init__(self):
        super().__init__("Credenciales de autenticación inválidas.")

class InsufficientPermissionsException(DomainException):
    def __init__(self):
        super().__init__("El usuario no posee permisos suficientes para ejecutar esta operación.")

class UserAlreadyExistsException(DomainException):
    def __init__(self, username: str):
        super().__init__(f"El usuario '{username}' ya se encuentra registrado.")

class InsufficientStockException(DomainException):
    def __init__(self, material_name: str, available: float, requested: float):
        super().__init__(f"Stock insuficiente para '{material_name}'. Disponible: {available}, solicitado: {requested}.")

class InvalidOrderStateException(DomainException):
    def __init__(self, message: str):
        super().__init__(message)
