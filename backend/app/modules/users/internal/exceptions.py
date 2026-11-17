from app.errors import ConflictError


class EmailAlreadyRegisteredError(ConflictError):
    def __init__(self) -> None:
        super().__init__("This email is already registered")
