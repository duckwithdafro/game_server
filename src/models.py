from pydantic import BaseModel
from starlette.websockets import WebSocket


class User(BaseModel):
    name: str
    current_world: str
    id: int


class UserConnection:
    def __init__(self, user: User, ws: WebSocket):
        self.user = user
        self.ws = ws

    async def send_event(
        self, event: "Event"
    ):  # the type of event is Event from events.py
        await self.ws.send_json(event)


class Message(BaseModel):
    """
    The message model. This is used to represent a message in the world.
    """

    user: User
    content: str
