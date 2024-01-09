
import uuid
from datetime import datetime

from genworlds.core.types import AgentState, Event
from genworlds.core.action import action
from genworlds.core.comms import event_mult
from genworlds.core.llm_calls import call_openai

@action
async def agent_replies_to_user(agent_state: AgentState, event: Event) -> AgentState:
    response = await call_openai("gpt-4", event.data, None, None)
    response_event = Event(agent_state.id, event.sender_id, created_at=datetime.now(), event_type="agent_replies_to_user", data=response)
    await event_mult.broadcast(response_event)
    new_agent_state = agent_state
    new_agent_state.memories.append(response_event)
    return new_agent_state

def basic_chat_assistant_generator(name: str) -> AgentState:
    return AgentState(
        id=str(uuid.uuid4())[:8],
        name="Basic Chat Assistant - " + name,
        description="An agent that helps users answering their questions",
        sub_types=[],
        memories=[],
        plan="",
        goals=[],
        llm_platform="openai",
        model_name="gpt-3.5-turbo",
        endpoint="",
        vars={},
        custom_state_updaters=[],
        actions={"agent_replies_to_user": agent_replies_to_user}
    )
