import asyncio
import uuid

from genworlds.core.types import WorldState
from genworlds.chat_utility_layer.assistant import basic_chat_assistant_generator
from genworlds.core.simulation import simulation

john = basic_chat_assistant_generator("John")

initial_world_state = WorldState(
    id=str(uuid.uuid4())[:8],
    name="Test World", 
    description="one agent world, test through postman or terminal",
    sub_types=[],
    agent_states={john.id: john},
    entity_states={},
    event_history=[],
    vars={},
    custom_state_updaters=[],
    actions={}
    )

asyncio.run(simulation(initial_world_state=initial_world_state))
