import asyncio
import websockets
import json

from genworlds.core.types import Event
from genworlds.core.utils import stringify_event

class EventMulticast:
    def __init__(self):
        self.subscribers = set()

    def subscribe(self, subscriber: asyncio.Queue):
        self.subscribers.add(subscriber)

    def unsubscribe(self, subscriber: asyncio.Queue):
        self.subscribers.discard(subscriber)

    async def broadcast(self, message):
        for subscriber in self.subscribers:
            await subscriber.put(message)

event_mult = EventMulticast() # Singleton

async def start_websocket_server():
    async def websocket_handler(websocket, path):
        ws_queue = asyncio.Queue()
        event_mult.subscribe(ws_queue)

        async def send_to_websocket():
            while True:
                message = await ws_queue.get()
                stringified_event = stringify_event(message)
                print("Event-chan -> WS:", stringified_event)
                await websocket.send(stringified_event)

        # Start a task to send messages to this websocket
        send_task = asyncio.create_task(send_to_websocket())

        try:
            async for message in websocket:
                parsed_message = Event(**json.loads(message))
                print("WS -> Event-chan:", parsed_message)
                await event_mult.broadcast(parsed_message)
        finally:
            # Clean up when the websocket connection is closed
            event_mult.unsubscribe(ws_queue)
            send_task.cancel()

    server = await websockets.serve(websocket_handler, "localhost", 7456)
    print("WebSocket server running on port 7456")
