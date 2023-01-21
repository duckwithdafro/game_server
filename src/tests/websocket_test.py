import traceback

from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket, WebSocketDisconnect

from src.main import app

# app = importlib.import_module('src.main', ).app


def main():
    client = TestClient(app)
    ws: WebSocket
    with client.websocket_connect("/api/ws") as ws:

        user = {"name": "test", "current_world": "", "id": 0}

        payload = {"world_name": "SpicyMackerel", "user": user}
        to_send = {"type": "user_join", "payload": payload}
        ws.send_json(to_send)
        to_send["payload"]["user"]["id"] = 1
        ws.send_json(to_send)
        while True:
            try:
                print(ws.receive_json())

            except WebSocketDisconnect as e:
                traceback.print_exc()


if __name__ == "__main__":
    main()
