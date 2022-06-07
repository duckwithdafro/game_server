import supertokens_python
from fastapi import FastAPI, Form
from starlette.requests import Request
from starlette.middleware.cors import CORSMiddleware

from starlette.websockets import WebSocket, WebSocketDisconnect
from supertokens_python.framework.fastapi import get_middleware
from supertokens_python.recipe import session

from src import models
from creds import ENV  # , SECRET_KEY
import asyncio

debug: bool = ENV == "dev"


app = FastAPI(debug=debug)  # disable docs for production?


data: models.Data = {
    "users": [],
    "channels": [],
    "websockets": [],
}


@app.middleware("http")  # for debugging purposes only - remove in production
async def http(request: Request, call_next):

    # print(app.state.websockets)
    return await call_next(request)


# add startup event handler
@app.on_event("startup")
async def startup():
    """
    This event handler is called when the server starts and adds cors middleware
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


# add shutdown event handler
@app.on_event("shutdown")
async def shutdown():
    """
    This event handler is called when the server shuts down
    """
    pass


# async def get_current_channel(request: Request):
#     """
#     This function returns the current channel based on the session
#     """
#     channel_id = request.session.get("channel_id")
#     if channel_id is None:
#         raise HTTPException(status_code=400, detail="Not logged in")
#
#     return models.Channel(id=channel_id)


# create web socket route for messages
@app.websocket("/api/messages/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    This endpoint handles websocket requests for messages
    """
    
    await websocket.accept()
    queue = asyncio.Queue()
    data["websockets"].append({'ws': websocket, 'queue': queue})
    # get current world
    
    
    try:
        while True:
            if not queue.empty():
                event = queue.get_nowait()
                await websocket.send_json(event)
    
            json_ = await websocket.receive_json()
            if message := json_.get("message"):
                print(message)
                
    except WebSocketDisconnect:
        pass
    
    finally:  # when the websocket disconnects or errors then remove it from the list
        data["websockets"].remove({'ws': websocket, 'queue': queue})
    
        print(data["websockets"])


# create login route for users to login and register
@app.post("/api/users/login")
async def login(email: str, password: str):
    """
    This endpoint handles login requests for users
    """
    return {"email": email, "password": password}


# create register route for users
@app.post("/api/users/register", status_code=201)
async def register(
    email: str = Form(...), username: str = Form(...), password: str = Form(...)
):
    """
    This endpoint handles registration requests for users
    """
    user = models.User(email=email, name=username, password=password)
    data["users"].append(user)


# create message route for messages to be posted with status_code HTTP_201_CREATED and only users in the same channel
# can post messages
# @app.post("/api/messages", status_code=fastapi.status.HTTP_201_CREATED)
# async def post_message(
#     request: Request,
#     message: str = Body(..., embed=True),
#     user: models.User = Depends(get_current_user),
#     channel: models.Channel = Depends(get_current_channel),
# ):
#     """
#     This endpoint handles posting messages
#     """
#     # add message to channel
#     if user in channel.users:
#         message = models.Message(content=message, user=user, channel=channel)
#         # get the ws from the channel
#         ws = data["websockets"][data["channels"].index(channel)]["ws"]
#         return {"message": message}
#     else:
#         raise HTTPException(
#             status_code=fastapi.status.HTTP_403_FORBIDDEN,
#             detail="You are not in this channel",
#         )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9000, debug=debug)
