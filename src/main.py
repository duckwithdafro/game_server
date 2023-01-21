from fastapi import Depends, FastAPI, WebSocket, WebSocketException, status
from pydantic import ValidationError
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocket, WebSocketDisconnect, WebSocketState

import worlds
from creds import DISCORD_CLIENT_ID, DISCORD_CLIENT_SECRET, ENV
from events import (
    EventType,
    UserJoinEvent,
    UserLeaveEvent,
    UserMessageEvent,
    UserMessagePayload,
)
from models import Message, User, UserConnection

debug: bool = ENV == "dev"


app = FastAPI(debug=debug)  # disable docs for production?


@app.on_event("startup")
async def startup():
    """
    This event handler is called when the server starts.

    It is used to initialize cors middleware.
    """

    # add cors middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
    )


async def on_ws_receive(data: dict, ws: WebSocket):
    """
    This on_ws_receive event handler is called when something is received on the websocket.
    """

    try:
        event_type = EventType(data["type"])
    except KeyError:
        raise WebSocketException(
            code=status.WS_1003_UNSUPPORTED_DATA,
            reason="Event is required for websockets",
        )
    except ValueError:
        raise WebSocketException(
            code=status.WS_1003_UNSUPPORTED_DATA,
            reason=f"Invalid event type \"{data['type']}\"",
        )

    if event_type == EventType.USER_JOIN:

        event = UserJoinEvent(**data)
        world_name = event.payload.world_name
        world = worlds.get_world(world_name)

        if world is None:
            raise worlds.NotInWorld(world_name)

        user = User(**data["payload"]["user"])
        user_connection = UserConnection(user, ws)

        if not world.user_in_world(user):
            await world.user_join(user_connection)
            await ws.send_json({"status": "success"})
        else:
            raise worlds.AlreadyInWorldError

    elif event_type == EventType.USER_LEAVE:

        event = UserLeaveEvent(**data)
        world_name = event.payload.world_name
        world = worlds.get_world(world_name)

        if world is None:
            raise HTTPException(status_code=404, detail="World not found")

        user = User(**data["payload"]["user"])

        if world.user_in_world(user):
            user_connection = world.connections[user.id]
            await world.user_leave(user_connection)
        else:
            raise worlds.NotInWorldError

    elif event_type == EventType.USER_MESSAGE:

        event = UserMessageEvent(**data)
        world_name = event.payload.world_name
        world = worlds.get_world(world_name)

        if world is None:
            raise HTTPException(status_code=404, detail="World not found")

        user = event.payload.message.user

        if world.user_in_world(user):
            await world.send_event(event)
        else:
            raise worlds.NotInWorldError

    else:
        print("this shouldnt hppen")


@app.websocket("/api/ws")
async def websocket(ws: WebSocket):
    """
    This websocket handler is called when a websocket connection is made.
    :param ws: The websocket connection
    """

    await ws.accept()

    try:
        while True:
            json_ = await ws.receive_json()
            await on_ws_receive(json_, ws)

    except WebSocketDisconnect:
        pass

    except ValidationError as e:
        await ws.send_json(e.json())
        print(e.json())
        print(e.args)

    except Exception as e:
        print(repr(e))

    finally:
        if not ws.client_state == WebSocketState.DISCONNECTED:
            await ws.close()


@app.get("/api/callback/discord")
async def discord_auth(code: str):
    print(code)


@app.post("/api/message")
async def post_message(message: Message):
    world = worlds.get_world(message.user.current_world)
    message_payload = UserMessagePayload(
        message=message, world_name=message.user.current_world
    )
    message_event = UserMessageEvent(payload=message_payload)
    if not world.user_in_world(message.user):
        raise worlds.NotInWorldError
    await world.send_event(message_event)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=9000)
