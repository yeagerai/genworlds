from typing import List
from yeager_core.events.base_event import Event
from yeager_core.events.event_decorators import event_type
from agents_creator_lab.objects.job import Job


@event_type("agent_reads_blackboard")
class AgentReadsBlackboardEvent(Event):
    description = "An agent reads the blackboard."
    agent_id: str
    blackboard_id: str


@event_type("blackboard_sends_content")
class BlackboardSendsContentEvent(Event):
    description = "The blackboard sends its content."
    agent_id: str
    blackboard_id: str
    blackboard_content: List[Job]


@event_type("agent_adds_job_to_blackboard")
class AgentAddsJobToBlackboardEvent(Event):
    description = "Agent adds a job to the blackboard."
    agent_id: str
    blackboard_id: str
    new_job: Job


@event_type("user_adds_job_to_blackboard")
class UserAddsJobToBlackboardEvent(Event):
    description = "User adds a job to the blackboard."
    agent_id: str
    blackboard_id: str
    new_job: Job


@event_type("agent_deletes_job_from_blackboard")
class AgentDeletesJobFromBlackboardEvent(Event):
    description = "An agent deletes a job from the blackboard."
    agent_id: str
    blackboard_id: str
    job_id: str
