import typing

from starlette.exceptions import HTTPException
from starlette.websockets import WebSocket

from events import (
    Event,
    EventType,
    UserJoinEvent,
    UserJoinPayload,
    UserLeaveEvent,
    UserLeavePayload,
)
from models import User, UserConnection


class AlreadyInWorldError(HTTPException):
    """
    This error is raised when a user tries to join a world they are already in.
    """

    status_code = 403  # forbidden
    detail = "You are already in this world."

    def __init__(self, user: User, world: str):
        # include the user and world in the headers
        headers = {"user": user, "world": world}
        super().__init__(
            status_code=self.status_code,
            detail=self.detail,
            headers=headers,
        )


class NotInWorldError(HTTPException):
    """
    This error is raised when a user tries to leave a world they are not in.
    """

    status_code = 403  # forbidden
    detail = "You are not in this world."

    def __init__(self, user: User, world: str):
        # include the user and world in the headers
        headers = {"user": str(user.id), "world": world}
        super().__init__(
            status_code=self.status_code, detail=self.detail, headers=headers
        )


class WorldBase:
    """
    The base class for all worlds.
    """

    def __init__(self):
        self.name = self.__class__.__name__
        self.connections: typing.List[UserConnection] = []

    async def send_event(self, event: Event):
        """
        Send an event to all users in the world.

        :param event: The Event() object to send.
        """

        for conn in self.connections:
            await conn.send_event(event)

    async def user_join(self, user: User, ws: WebSocket):
        """
        Add a user to the world.

        :param user: The user to add.
        :param ws: The websocket connection of the user.
        """

        connection_data = UserConnection(user, ws)
        self.connections.append(connection_data)
        payload = UserJoinPayload(user=user, world_name=self.name)
        # send user join event to all users
        event = UserJoinEvent(
            type=EventType.USER_JOIN,
            payload=payload,
        )
        await self.send_event(event)

    async def user_leave(self, user: User, ws: WebSocket):
        """
        Remove a user from the world.

        :param user: The user to remove.
        :param ws: The websocket connection of the user.
        """

        self.connections.remove(UserConnection(user, ws))
        # send user leave event to all users
        payload = UserLeavePayload(user=user, world_name=self.name)
        event = UserLeaveEvent(
            type=EventType.USER_LEAVE,
            payload=payload,
        )
        await self.send_event(event)

    def user_in_world(self, user: User):
        """
        Check if a user is in the world.

        :param user: The user to check.
        :return: True if the user is in the world, False otherwise.
        """
        # iterate over the users in the world
        for conn in self.connections:
            # check by id
            if conn.user.id == user.id:
                return True
        return False


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
