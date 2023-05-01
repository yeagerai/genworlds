from typing import List

from yeager_core.worlds.base_world import BaseObject
from yeager_core.events.base_event import EventDict, EventHandler
from yeager_core.objects.base_object import BaseObject
from yeager_core.properties.basic_properties import Coordinates, Size
from yeager_core.events.base_event import Listener
from agents_creator_lab.events import (
    AgentReadsBlackboardEvent,
    AgentDeletesJobFromBlackboardEvent,
    AgentAddsJobToBlackboardEvent,
    BlackboardSendsContentEvent,
)
from agents_creator_lab.objects.job import Job


class Blackboard(BaseObject):
    def __init__(
        self,
        name: str,
        description: str,
        position: Coordinates,
        size: Size,
        event_dict: EventDict,
        event_handler: EventHandler,
        important_event_types: List[str],
    ):
        important_event_types.extend(
            [
                "agent_reads_blackboard",
                "agent_adds_job_to_blackboard",
                "agent_deletes_job_from_blackboard",
                "user_adds_job_to_blackboard",
            ]
        )

        event_handler.register_listener(
            event_type="agent_reads_blackboard",
            listener=Listener(
                name="agent_reads_blackboard_listener",
                description="Listens for an agent requesting blackboard content.",
                function=self.agent_reads_blackboard_listener,
            ),
        )
        event_handler.register_listener(
            event_type="agent_adds_job_to_blackboard",
            listener=Listener(
                name="agent_adds_job_to_blackboard_listener",
                description="Listens for an agent adding a job to the blackboard.",
                function=self.agent_adds_job_to_blackboard_listener,
            ),
        )

        event_handler.register_listener(
            event_type="user_adds_job_to_blackboard",
            listener=Listener(
                name="user_adds_job_to_blackboard_listener",
                description="Listens for a user adding a job to the blackboard.",
                function=self.user_adds_job_to_blackboard_listener,
            ),
        )

        event_handler.register_listener(
            event_type="agent_deletes_job_from_blackboard",
            listener=Listener(
                name="agent_deletes_job_from_blackboard_listener",
                description="Listens for an agent deleting a job from the blackboard.",
                function=self.agent_deletes_job_from_blackboard_listener,
            ),
        )

        super().__init__(
            name,
            description,
            position,
            size,
            event_dict,
            event_handler,
            important_event_types,
        )
        self.content: List[Job] = []

    def _add_job(self, new_job: Job):
        self.content.append(new_job)

    def _delete_job(self, job_id: str):
        self.content = [job for job in self.content if job.id != job_id]

    async def agent_reads_blackboard_listener(self, event: AgentReadsBlackboardEvent):
        blackboard_content = BlackboardSendsContentEvent(
            agent_id=event.agent_id,
            object_id=self.id,
            blackboard_jobs=self.content,
        )
        await self.world_socket_client.send_message(blackboard_content.json())

    async def agent_deletes_job_from_blackboard_listener(
        self, event: AgentDeletesJobFromBlackboardEvent
    ):
        self._delete_job(event.job_id)

    async def agent_adds_job_to_blackboard_listener(
        self, event: AgentAddsJobToBlackboardEvent
    ):
        self._add_job(event.new_job)

    async def user_adds_job_to_blackboard_listener(
        self, event: AgentAddsJobToBlackboardEvent
    ):
        self._add_job(event.new_job)
