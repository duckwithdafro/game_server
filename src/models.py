from typing import List, TypedDict, Dict
from starlette.websockets import WebSocket

from pydantic import BaseModel


class Message(BaseModel):
    content: str
    user: "User"


class World(BaseModel):
    users: List["User"] = []
    messages: List["Message"] = []
    ws: "WebSocket"


class User(BaseModel):
    id: str
    name: str


class Data(TypedDict):
    users: List["User"]
    worlds: List["World"]
    websockets: List[Dict]
