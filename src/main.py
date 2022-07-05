import supertokens_python
from fastapi import Depends, FastAPI
from pydantic import ValidationError
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocket, WebSocketDisconnect, WebSocketState
from supertokens_python.framework.fastapi import get_middleware
from supertokens_python.recipe import session, thirdpartyemailpassword
from supertokens_python.recipe.session import SessionContainer
from supertokens_python.recipe.session.framework.fastapi import verify_session
from supertokens_python.recipe.thirdpartyemailpassword import Discord

import worlds
from creds import (
    DISCORD_CLIENT_ID,
    DISCORD_CLIENT_SECRET,
    ENV,
    ST_API_KEY,
    ST_CONNECTION_URI,
)
from events import (
    EventType,
    UserJoinEvent,
    UserLeaveEvent,
    UserMessageEvent,
    UserMessagePayload,
)
from models import Message, User

debug: bool = ENV == "dev"


app = FastAPI(debug=debug)  # disable docs for production?


@app.on_event("startup")
async def startup():
    """
    This event handler is called when the server starts.

    It is used to initialize supertokens and cors middleware.
    """

    # supertokens setup things

    app.add_middleware(get_middleware())
    supertokens_python.init(
        supertokens_config=supertokens_python.SupertokensConfig(
            connection_uri=ST_CONNECTION_URI, api_key=ST_API_KEY
        ),
        app_info=supertokens_python.InputAppInfo(
            app_name="game",
            api_domain="http://localhost:9000",
            website_domain="http://localhost:3000",
            api_base_path="/api",
            website_base_path="/",
        ),
        framework="fastapi",
        recipe_list=[
            session.init(),
            thirdpartyemailpassword.init(
                providers=[
                    Discord(
                        client_id=DISCORD_CLIENT_ID, client_secret=DISCORD_CLIENT_SECRET
                    )
                ]
            ),
        ],
        telemetry=False,
    )

    # add cors middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=supertokens_python.get_all_cors_headers(),
    )


async def on_ws_receive(data: dict, ws: WebSocket):
    """
    This on_ws_receive event handler is called when something is received on the websocket.
    """
    # make a test user from dict
    # user = {
    #     "name": "test user",
    #     "current_world": "SpicyMackerel",
    #     "id": 1,
    # }
    #
    # # create a message from dict
    # message = {
    #     "user": user,
    #     "content": "test message",
    # }
    #
    # # create a message payload from dict
    # message_payload = {
    #     "message": message,
    #     "world_name": "SpicyMackerel",
    # }
    #
    # # create a message event from dict
    # message_event = {
    #     "type": EventType.USER_MESSAGE,
    #     "payload": message_payload,
    # }
    #
    # # create a message model
    # message_model = UserMessageEvent(**message_event)

    if data["type"] == EventType.USER_JOIN.value:
        # convert the data to a UserJoinEvent
        event = UserJoinEvent(**data)
        # get world name from event
        world_name = event.payload.world_name
        # get the world object
        world = worlds.get_world(world_name)
        if world is None:
            # world doesn't exist
            raise HTTPException(status_code=404, detail="World not found")
        # create a user object
        user = User(**data["payload"]["user"])
        # check if the user is already in the world
        if not world.user_in_world(user):
            # add the user to the world
            await world.user_join(user, ws)
        else:
            # error, user already in world
            raise worlds.AlreadyInWorldError(user, world_name)

    elif data["type"] == EventType.USER_LEAVE.value:
        # convert the data to a UserLeaveEvent
        event = UserLeaveEvent(**data)
        # get world name from event
        world_name = event.payload.world_name
        # get the world object
        world = worlds.get_world(world_name)
        if world is None:
            # world doesn't exist, send error to websocket
            raise HTTPException(status_code=404, detail="World not found")

        # get the user object
        user = User(**data["payload"]["user"])
        # check if the user is in the world
        if world.user_in_world(user):
            # remove the user from the world
            await world.user_leave(user, ws)
        else:
            # error, user not in world
            raise worlds.NotInWorldError(user, world_name)

    elif data["type"] == EventType.USER_MESSAGE.value:
        # convert the data to a UserMessageEvent
        event = UserMessageEvent(**data)

        # get world name from event
        world_name = event.payload.world_name
        # get the world object
        world = worlds.get_world(world_name)
        if world is None:
            # world doesn't exist, send error to websocket
            raise HTTPException(status_code=404, detail="World not found")
        # get the user object
        user = event.payload.message.user
        # check if the user is in the world
        if world.user_in_world(user):
            # send the message to the world
            await world.send_event(event)
        else:
            # error, user not in world
            raise worlds.NotInWorldError(user, world_name)

    else:
        # error, unprocessable entity
        raise HTTPException(status_code=422, detail="Unprocessable entity")


@app.websocket("/api/ws")
async def websocket(ws: WebSocket):
    """
    This websocket handler is called when a websocket connection is made.
    :param ws: The websocket connection
    """

    await ws.accept()

    try:
        while True:
            # process messages from the client
            json_ = await ws.receive_json()
            # print(json_)
            await on_ws_receive(json_, ws)

    except WebSocketDisconnect:
        pass

    except ValidationError as e:
        await ws.send_json(e.json())
        print(e.json())
        print(e.args)

    finally:
        if not ws.client_state == WebSocketState.DISCONNECTED:
            await ws.close()


@app.get("/api/callback/discord")
async def discord_auth(code: str):
    print(code)


@app.get("/session")
async def session_info(sess: SessionContainer = Depends(verify_session())):
    return {
        "session_handle": sess.get_handle(),
        "user_id": sess.get_user_id(),
        "access_token_payload": sess.get_access_token_payload(),
    }


@app.post("/api/message")
async def post_message(message: Message):
    world = worlds.get_world(message.user.current_world)
    message_payload = UserMessagePayload(
        message=message, world_name=message.user.current_world
    )
    message_event = UserMessageEvent(payload=message_payload)
    if not world.user_in_world(message.user):
        raise worlds.NotInWorldError(message.user, message.user.current_world)
    await world.send_event(message_event)


@app.post("/api/join")
async def join(user: User, world: str):
    # token
    pass


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9000, debug=debug)
