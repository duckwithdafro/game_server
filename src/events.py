from enum import Enum

# create event enums
from pydantic import BaseModel


class EventType(Enum):
    USER_JOIN = "user_join"
    USER_LEAVE = "user_leave"
    MESSAGE = "message"


user_join = EventType.USER_JOIN
user_leave = EventType.USER_LEAVE
message = EventType.MESSAGE


# create event model
class Event(BaseModel):
    type: EventType
    # payload can contain different data depending on the event type
    payload: dict
