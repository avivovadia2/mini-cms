from app.errors import ConflictError, NotFoundError


class FnolNotFoundError(NotFoundError):
    # Also raised for another organization's FNOL: never confirm that the id exists.
    def __init__(self) -> None:
        super().__init__("FNOL not found")


class FnolNotSubmittedError(ConflictError):
    """Only a submitted FNOL can change status; converted and rejected are final."""

    def __init__(self, status: str) -> None:
        super().__init__(f"This FNOL is already {status}")
