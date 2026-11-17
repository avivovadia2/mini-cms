from app.errors import ConflictError, NotFoundError


class PolicyNotFoundError(NotFoundError):
    # Also raised for another organization's policy: never confirm that the id exists.
    def __init__(self) -> None:
        super().__init__("Policy not found")


class PolicyNumberAlreadyExistsError(ConflictError):
    def __init__(self) -> None:
        super().__init__("A policy with this number already exists")
