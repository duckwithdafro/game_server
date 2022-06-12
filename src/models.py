from pydantic import BaseModel


class User(BaseModel):
    name: str
    current_world: str
    id: int


class Message(BaseModel):
    """
    The message model. This is used to represent a message in the world.
    """

    user: User
    content: str
