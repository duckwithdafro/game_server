from pydantic import BaseModel


class User(BaseModel):
    username: str
    current_world: str
    id: int


class Message(BaseModel):
    """
    The message model. This is used to represent a message in the world.
    """

    sender: User
    content: str
