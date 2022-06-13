import supertokens_python
from fastapi import FastAPI
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocket, WebSocketDisconnect, WebSocketState
from supertokens_python.framework.fastapi import get_middleware
from supertokens_python.recipe import session

import worlds
from creds import ENV
from events import EventType, UserJoinEvent, UserLeaveEvent
from models import User

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
            connection_uri="http://localhost:3567"
        ),
        app_info=supertokens_python.InputAppInfo(
            app_name="game",
            api_domain="http://localhost:9000",
            website_domain="http://localhost:3000",
        ),
        framework="fastapi",
        recipe_list=[session.init()],
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
    # process the data for events
    if data["type"] == EventType.USER_JOIN:
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
    elif data["type"] == EventType.USER_LEAVE:
        # convert the data to a UserLeaveEvent
        event = UserLeaveEvent(**data)
        # get world name from event
        world_name = event.payload.world_name
        # get the world object
        world = worlds.get_world(world_name)
        if world is None:
            # world doesn't exist
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
            await on_ws_receive(json_, ws)

    except WebSocketDisconnect:
        pass

    finally:
        if not ws.client_state == WebSocketState.DISCONNECTED:
            await ws.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9000, debug=debug)
