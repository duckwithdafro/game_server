from typing import List, TypedDict

from pydantic import BaseModel


class Message(BaseModel):
    content: str
    user: "User"


class Channel(BaseModel):
    id: str
    users: List["User"] = []
    messages: List["Message"] = []


class User(BaseModel):
    id: str
    name: str
    email: str


class Data(TypedDict):
    users: List["User"]
    channels: List["Channel"]
    websockets: List[str]
