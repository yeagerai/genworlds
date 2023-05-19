from typing import List
from genworlds.events.websocket_event_handler import Event
from use_cases.roundtable.objects.job import Job


class AgentReadsBlackboardEvent(Event):
    event_type = "agent_reads_blackboard"
    description = "An agent reads the blackboard."


class BlackboardSendsContentEvent(Event):
    event_type = "blackboard_sends_content"
    description = "The blackboard sends its content."
    blackboard_content: List[Job]


class AgentAddsJobToBlackboardEvent(Event):
    event_type = "agent_adds_job_to_blackboard"
    description = "Agent adds a job to the blackboard."
    new_job: Job


class UserAddsJobToBlackboardEvent(Event):
    event_type = "user_adds_job_to_blackboard"
    description = "User adds a job to the blackboard."
    new_job: Job


class AgentDeletesJobFromBlackboardEvent(Event):
    event_type = "agent_deletes_job_from_blackboard"
    description = "An agent deletes a job from the blackboard."
    job_id: str
