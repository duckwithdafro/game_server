import typing

from fastapi import WebSocket, WebSocketException, status
from starlette.exceptions import HTTPException

from events import (
    Event,
    EventType,
    UserJoinEvent,
    UserJoinPayload,
    UserLeaveEvent,
    UserLeavePayload,
)
from models import User, UserConnection


class AlreadyInWorldError(WebSocketException):
    """
    This error is raised when a user tries to join a world they are already in.
    """

    code = status.WS_1003_UNSUPPORTED_DATA
    reason = "You are already in this world."

    def __init__(self):
        super().__init__(code=self.code, reason=self.reason)

    def __str__(self):
        return self.reason


class NotInWorldError(WebSocketException):
    """
    This error is raised when a user tries to leave a world they are not in.
    """

    code = status.WS_1003_UNSUPPORTED_DATA
    reason = "You are not in this world."

    def __init__(self):
        super().__init__(code=self.code, reason=self.reason)


class NotInWorld(WebSocketException):
    code = status.WS_1003_UNSUPPORTED_DATA
    reason = '"{world_name}" is not a valid world.'

    def __init__(self, world_name):
        super().__init__(
            code=self.code, reason=self.reason.format(world_name=world_name)
        )


class WorldBase:
    """
    The base class for all worlds.
    """

    def __init__(self):
        self.name = self.__class__.__name__
        self.connections: dict[int, UserConnection] = {}

    async def send_event(self, event: Event):
        """
        Send an event to all users in the world.

        :param event: The Event() object to send.
        """

        for conn in self.connections.values():
            await conn.send_event(event)

    async def user_join(self, conn: UserConnection):
        """
        Add a user to the world.


        """

        # connection_data = UserConnection(user, ws)
        self.connections[conn.id] = conn
        payload = UserJoinPayload(user=conn.user, world_name=self.name)
        # send user join event to all users
        event = UserJoinEvent(
            type=EventType.USER_JOIN,
            payload=payload,
        )
        await self.send_event(event)

    async def user_leave(self, conn: UserConnection):
        """
        Remove a user from the world.

        """

        self.connections.pop(conn.id)
        # send user leave event to all users
        payload = UserLeavePayload(user=conn.user, world_name=self.name)
        event = UserLeaveEvent(
            type=EventType.USER_LEAVE,
            payload=payload,
        )
        await self.send_event(event)

    def user_in_world(self, conn) -> bool:
        """
        Check if a user is in the world.

        :return: True if the user is in the world, False otherwise.
        """
        return any(conn.id == c.id for c in self.connections.values())


class SpicyMackerel(WorldBase):
    """
    The SpicyMackerel world.
    """

    pass


_worlds = {"SpicyMackerel": SpicyMackerel()}  # type: typing.Dict[str, WorldBase]


def get_world(name: str) -> typing.Optional[WorldBase]:
    """
    Get a world by name.

    :param name: The name of the world.
    :return: The world.
    """
    return _worlds.get(name)
