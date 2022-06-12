from enum import Enum

from pydantic import BaseModel


class EventType(Enum):
    USER_JOIN = "user_join"
    USER_LEAVE = "user_leave"
    MESSAGE = "message"


class Event(BaseModel):
    type: EventType
    # payload can contain different data depending on the event type
    payload: dict
