from enum import Enum

from pydantic import BaseModel

from models import Message, User


class EventType(str, Enum):
    USER_JOIN = "user_join"
    USER_LEAVE = "user_leave"
    USER_MESSAGE = "user_message"

    @classmethod
    def from_str(cls, string: str):
        return getattr(cls, string.lower())


class PayloadBase(BaseModel):
    pass


class UserJoinPayload(PayloadBase):
    user: User
    world_name: str


class UserLeavePayload(PayloadBase):
    user: User
    world_name: str


class UserMessagePayload(PayloadBase):
    message: Message
    world_name: str


class Event(BaseModel):
    type: EventType
    # payload can contain different data depending on the event type
    payload: PayloadBase


class UserJoinEvent(Event):
    type = EventType.USER_JOIN
    payload: UserJoinPayload


class UserLeaveEvent(Event):
    type = EventType.USER_LEAVE
    payload: UserLeavePayload


class UserMessageEvent(Event):
    type = EventType.USER_MESSAGE
    payload: UserMessagePayload
