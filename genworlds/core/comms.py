from typing import Set
import asyncio
import websockets
import json

from genworlds.core.types import Event
from genworlds.core.utils import stringify_event

class EventMulticast:
    def __init__(self):
        self.subscribers:Set[asyncio.Queue] = set()

    def subscribe(self, subscriber: asyncio.Queue):
        self.subscribers.add(subscriber)

    def unsubscribe(self, subscriber: asyncio.Queue):
        self.subscribers.discard(subscriber)

    async def broadcast(self, message):
        for subscriber in self.subscribers:
            await subscriber.put(message)

event_mult = EventMulticast() # Singleton

async def start_websocket_server():
    ws_queue = asyncio.Queue()
    event_mult.subscribe(ws_queue)
    connected_websockets = set()

    async def send_to_all_clients():
        while True: 
            message = await ws_queue.get()
            stringified_event = stringify_event(message)
            print("Event-chan -> WS:", stringified_event)
            disconnected_sockets = set()
            for websocket in connected_websockets:
                if websocket.open:
                    try:
                        await websocket.send(stringified_event)
                    except websockets.exceptions.ConnectionClosed:
                        disconnected_sockets.add(websocket)
            for websocket in disconnected_sockets:
                connected_websockets.discard(websocket)

    async def websocket_handler(websocket, path):
        connected_websockets.add(websocket)
        try:
            async for message in websocket:
                parsed_message = Event(**json.loads(message))
                print("WS -> Event-chan:", parsed_message)
                await event_mult.broadcast(parsed_message)
        finally:
            connected_websockets.discard(websocket)

    asyncio.create_task(send_to_all_clients())
    server = await websockets.serve(websocket_handler, "localhost", 7456)
    print("WebSocket server running on port 7456")
    await server.wait_closed()
