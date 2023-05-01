from typing import List
from yeager_core.events.base_event import Event
from agents_creator_lab.objects.job import Job


class AgentReadsBlackboardEvent(Event):
    event_type = "agent_reads_blackboard"
    description = "An agent reads the blackboard."
    agent_id: str
    blackboard_id: str


class BlackboardSendsContentEvent(Event):
    event_type = "blackboard_sends_content"
    description = "The blackboard sends its content."
    agent_id: str
    blackboard_id: str
    blackboard_content: List[Job]


class AgentAddsJobToBlackboardEvent(Event):
    event_type = "agent_adds_job_to_blackboard"
    description = "Agent adds a job to the blackboard."
    agent_id: str
    blackboard_id: str
    new_job: Job


class UserAddsJobToBlackboardEvent(Event):
    event_type = "user_adds_job_to_blackboard"
    description = "User adds a job to the blackboard."
    agent_id: str
    blackboard_id: str
    new_job: Job


class AgentDeletesJobFromBlackboardEvent(Event):
    event_type = "agent_deletes_job_from_blackboard"
    description = "An agent deletes a job from the blackboard."
    agent_id: str
    blackboard_id: str
    job_id: str
