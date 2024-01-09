import asyncio
from asyncio import create_task
from genworlds.core.types import WorldState

from genworlds.core.entity import entity, world
from genworlds.core.agent import agent
from genworlds.core.comms import start_websocket_server

async def simulation(initial_world_state: WorldState):
    print(f"\n{initial_world_state}\n")

    await start_websocket_server()

    print("Starting simulation...")

    create_task(world(initial_world_state.id, initial_world_state))

    for entity_state in initial_world_state.entity_states.values():
        create_task(entity(entity_state.id))
    
    for agent_state in initial_world_state.agent_states.values():
        create_task(agent(agent_state.id))

    print("Simulation is running...")
    while True:
        await asyncio.sleep(1)