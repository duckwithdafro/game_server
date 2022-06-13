import typing
from enum import Enum

from pydantic import BaseModel

from models import Message, User


class EventType(Enum):
    USER_JOIN = "user_join"
    USER_LEAVE = "user_leave"
    MESSAGE = "message"


class PayloadBase(BaseModel):
    pass


class UserJoinPayload(PayloadBase):
    user: User
    world_name: str


class UserLeavePayload(PayloadBase):
    user: User
    world_name: str


class MessagePayload(PayloadBase):
    message: Message


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


class MessageEvent(Event):
    type = EventType.MESSAGE
    payload: MessagePayload
