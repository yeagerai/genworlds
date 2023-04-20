import json
import asyncio

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from yeager_core.worlds.base_world import BaseWorld
from .world_agents.y_tools import ytools
from .world_objects.blackboard import blackboard

app = FastAPI()

world = BaseWorld(
    name="agents_creator_lab",
    description="This is a lab where agents can be created",
    objects=[blackboard],
    agents=[ytools],
)

world.launch()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        world_state = world.serialize_state()
        await websocket.send_text(world_state)
        await asyncio.sleep(1)  # Send the world state every second

@app.get("/")
async def get():
    return HTMLResponse(
        """
        <!DOCTYPE html>
        <html>
            <head>
                <title>World Visualization</title>
            </head>
            <body>
                <script>
                    const socket = new WebSocket("ws://localhost:8000/ws");

                    socket.onmessage = (event) => {
                        const worldState = JSON.parse(event.data);
                        console.log(worldState);
                        // Render the world state visually here
                    };
                </script>
            </body>
        </html>
        """
    )

# To execute the world, run the following command:
# uvicorn main:app --reload 