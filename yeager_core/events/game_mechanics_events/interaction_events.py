from pydantic import BaseModel

class BaseAOInteractionEvent(BaseModel):
    """
    Base Agent Object Interaction Event
    """
    event_type = "agent_object_interaction"
    object_id: str
    initiator_id: str

class InspectObjectEvent(BaseAOInteractionEvent):
    event_subtype = "agent_inspects_object"

class UseObjectEvent(BaseAOInteractionEvent):
    event_subtype = "agent_uses_object"

class ActivateObjectEvent(BaseAOInteractionEvent):
    event_subtype = "agent_activates_object"

class PickUpObjectEvent(BaseAOInteractionEvent):
    event_subtype = "agent_picksup_object"

class BaseAAInteractionEvent(BaseModel):
    """
    Base Agent Agent Interaction Event
    """
    event_type = "agent_agent_interaction"
    initiator_id: str
    receiver_id: str

class BaseUOInteractionEvent(BaseModel):
    """
    Base User Object Interaction Event
    """
    event_type = "user_object_interaction"
    object_id: str
    user_id: str