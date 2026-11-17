from app.errors import NotFoundError


class OrganizationNotFoundError(NotFoundError):
    def __init__(self) -> None:
        super().__init__("Organization not found")
