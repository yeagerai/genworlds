from typing import List
from pydantic import BaseModel
from yeager_core.worlds.base_world import BaseObject
from yeager_core.events.game_mechanics_events.interaction_events import UseObjectEvent, BaseUOInteractionEvent

# Components
class Job(BaseModel):
    id: str
    description: str
    assigned_to: str
    output_format: str
    status: str

# Events
class UserAddsJobEvent(BaseUOInteractionEvent):
    job: Job

class AgentReadsJobsEvent(UseObjectEvent):
    asigned_backboard_jobs: List[Job]

class AgentUpdatesJobStatusEvent(UseObjectEvent):
    job_id: str
    job_status: str

class UserDeletesJobEvent(BaseUOInteractionEvent):
    job_id: str

# Main Class
class Blackboard(BaseObject):
    content: List[Job]

    def _add_job(self, new_job: Job):
        self.content.append(new_job)
    
    def _delete_job(self, job_id: str):
        self.content = [job for job in self.content if job.id != job_id]
    
    def handle_user_adds_job(self, event: UserAddsJobEvent):
        self._add_job(event.job)

    def handle_user_deletes_job(self, event: UserDeletesJobEvent):
        self._delete_job(event.job_id)
    
    def handle_agent_reads_jobs(self, event: AgentReadsJobsEvent):
        event.asigned_backboard_jobs = self.content