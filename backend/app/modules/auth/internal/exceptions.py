from app.errors import AuthenticationError


class InvalidCredentialsError(AuthenticationError):
    # One message for unknown email, wrong password and inactive user, so a failed login doesn't
    # reveal which emails are registered.
    def __init__(self) -> None:
        super().__init__("Invalid email or password")
