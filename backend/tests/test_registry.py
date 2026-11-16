import pytest

from app.registry import get_service, register_service


class GreeterInterface:
    pass


class Greeter(GreeterInterface):
    pass


class WelcomerInterface:
    pass


class Welcomer(WelcomerInterface):
    def __init__(self, greeter: GreeterInterface) -> None:
        self.greeter = greeter


class PingInterface:
    pass


class PongInterface:
    pass


class Ping(PingInterface):
    def __init__(self, pong: PongInterface) -> None:
        self.pong = pong


class Pong(PongInterface):
    def __init__(self, ping: PingInterface) -> None:
        self.ping = ping


class UnregisteredInterface:
    pass


class TestRegistry:
    def test_injects_constructor_dependencies_by_interface(self) -> None:
        register_service(GreeterInterface, Greeter)
        register_service(WelcomerInterface, Welcomer)

        welcomer = get_service(WelcomerInterface)

        assert isinstance(welcomer, Welcomer)
        assert welcomer.greeter is get_service(GreeterInterface)

    def test_returns_the_same_instance_every_time(self) -> None:
        register_service(GreeterInterface, Greeter)

        assert get_service(GreeterInterface) is get_service(GreeterInterface)

    def test_unregistered_interface_raises(self) -> None:
        with pytest.raises(LookupError):
            get_service(UnregisteredInterface)

    def test_circular_dependency_raises(self) -> None:
        register_service(PingInterface, Ping)
        register_service(PongInterface, Pong)

        with pytest.raises(RuntimeError, match="Circular"):
            get_service(PingInterface)
