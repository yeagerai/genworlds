import json
import asyncio

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from yeager_core.worlds.base_world import BaseWorld
from .agents.y_tools import ytools
from .objects.blackboard import Blackboard

app = FastAPI()

blackboard = Blackboard(
    name="blackboard",
    description="The blackboard is a place where agents can read and write all the jobs they have to do while in the lab",
    content=[],
)

ytools = ...

world = BaseWorld(
    name="agents_creator_lab",
    description="This is a lab where agents can be created",
    objects=[blackboard],
    agents=[ytools],
)

asyncio.create_task(world.launch())


@app.websocket("/ws/world")
async def websocket_endpoint(websocket: WebSocket):
    await world.websocket_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Process data received from the agent, if needed
    except WebSocketDisconnect:
        world.websocket_manager.disconnect(websocket)


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
