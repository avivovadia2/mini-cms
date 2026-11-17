from app.errors import ConflictError, NotFoundError


class EmailAlreadyRegisteredError(ConflictError):
    def __init__(self) -> None:
        super().__init__("This email is already registered")


class UserNotFoundError(NotFoundError):
    # Also raised for a user of another organization: never confirm that the id exists.
    def __init__(self) -> None:
        super().__init__("User not found")
