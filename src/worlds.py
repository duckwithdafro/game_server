import asyncio
import typing

from starlette.exceptions import HTTPException

from models import Message, User
from events import Event, EventType


class AlreadyInWorldError(HTTPException):
    # forbidden
    status_code = 403
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
    # forbidden
    status_code = 403
    detail = "You are not in this world."

    def __init__(self, user: User, world: str):
        # include the user and world in the headers
        headers = {"user": user, "world": world}
        super().__init__(
            status_code=self.status_code, detail=self.detail, headers=headers
        )


class WorldBase:
    """
    The base class for all worlds.
    """

    def __init__(self):
        self.name = self.__class__.__name__
        self.connections = []

    async def send_event(self, event: Event):
        """
        Send an event to all users in the world.
        :param event: The Event() object to send.
        """
        # create event
        
        for conn in self.connections:
            ws = conn["ws"]
            user = conn["user"]
            

    async def user_join(self, user: User):
        """
        Add a user to the world.
        :param user: The user to add.
        """
        self.users.append(user)
        await self.send_message(f"{user.name} has joined the world.")

    async def user_leave(self, user: User):
        """
        Remove a user from the world.
        :param user: The user to remove.
        """
        self.users.remove(user)
        # send user join event to all users
        

    def user_in_world(self, user: User):
        """
        Check if a user is in the world.
        :param user: The user to check.
        :return: True if the user is in the world, False otherwise.
        """
        # iterate over the users in the world
        for u in self.users:
            # check by id
            if u.id == user.id:
                return True
        return False


class SpicyMackerel(WorldBase):
    """
    The SpicyMackerel world.
    """

    pass


_worlds = {"SpicyMackerel": SpicyMackerel()}  # type: typing.Dict[str, WorldBase]


def get_world(name: str) -> WorldBase:
    """
    Get a world by name.
    :param name: The name of the world.
    :return: The world.
    """
    return _worlds[name]
