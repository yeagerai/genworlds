import os
from typing import List
import uuid
from time import sleep

import json
import platform

from langchain import PromptTemplate, LLMChain
from langchain.chat_models import ChatOpenAI

from genworlds.objects.abstracts.object import AbstractObject
from genworlds.events.abstracts.event import AbstractEvent
from genworlds.events.abstracts.action import AbstractAction


class UserRequestsScreensToWorldEvent(AbstractEvent):
    event_type = "user_requests_screens_to_world"
    description = "The user requests the screens to the world."


class WorldSendsScreensToUserEvent(AbstractEvent):
    event_type = "world_sends_screens_to_user"
    description = "The world sends the screens to the user."
    screens_config: dict


class WorldSendsScreensToUser(AbstractAction):
    trigger_event_class = UserRequestsScreensToWorldEvent
    description = "The world sends the screens to the user."

    def __init__(self, host_object: AbstractObject):
        super().__init__(host_object=host_object)

    def __call__(self, event: UserRequestsScreensToWorldEvent):
        with open(self.host_object.screens_config_path) as f:
            screens_config = json.load(f)

        event = WorldSendsScreensToUserEvent(
            sender_id=self.host_object.id,
            screens_config=screens_config,
        )
        self.host_object.send_event(event)

class UserStopsSessionEvent(AbstractEvent):
    event_type="user_stops_session_event"
    description="The user wants to stop the current session"
    session_id: str

class UserStopsSession(AbstractAction):
    trigger_event_class=UserStopsSessionEvent
    description="The user wants to stop the current session"
    def __init__(self, host_object: AbstractObject):
        super().__init__(host_object=host_object)

    def __call__(self, event: UserStopsSessionEvent):
        # store all agents and objects states and memories
        # store all event history
        pass

class UserStartsNewSessionEvent(AbstractEvent):
    event_type="user_starts_new_session_event"
    description = "The user wants to start a new session."
    session_first_message: str

class WorldSendsSessionDetialsToUserEvent(AbstractEvent):
    event_type="user_starts_new_session_event"
    description = "The user wants to start a new session."
    session_name: str
    session_id: str

class UserStartsNewSession(AbstractAction):
    trigger_event_class = UserStartsNewSessionEvent
    description = "The user wants to start a new session."

    def __init__(self, host_object: AbstractObject):
        super().__init__(host_object=host_object)
        self.summary_template = """
        This is The first message coming from a user that wants to start a conversation:
        {event}
        Give me in three to five words the topic of the conversation.
        """

        self.summary_prompt = PromptTemplate(
            template=self.summary_template,
            input_variables=[
                "event",
            ],
        )

        self.chat = ChatOpenAI(
            temperature=0, model_name="gpt-3.5-turbo-1106", openai_api_key=os.environ.get("OPENAI_API_KEY")
        )
        self.chain = LLMChain(llm=self.chat, prompt=self.summary_prompt)

    def summarize_message(self, session_first_message: str) -> str:
        return self.chain.run(session_first_message)

    def get_ip_based_on_os() -> str:
        if platform.system() == "Windows":
            return "127.0.0.1"
        else:
            return "0.0.0.0"
    
    def __call__(self, event: UserStartsNewSessionEvent):
        session_name = self.summarize_message(event.session_first_message)
        session_id = str(uuid.uuid4())

        if not os.path.exists(self.host_object.sessions_storage_path):
            os.makedirs(self.host_object.sessions_storage_path)
        session_path = os.path.join(self.host_object.sessions_storage_path, session_id)
        os.makedirs(session_path)

        session_details_event = WorldSendsSessionDetialsToUserEvent(
            session_name=session_name, 
            session_id=session_id,
        )
        self.host_object.send_event(session_details_event)

        sleep(0.5) # give time for frontend to parse message

        self.host_object.terminate()
        self.host_object.launch(host=self.get_ip_based_on_os())

class UserLoadsSessionEvent(AbstractEvent):
    event_type="user_loads_session_event"
    description = "The user wants to load a previous session."
    session_id: str

class WorldSendsSessionEvent(AbstractEvent):
    event_type="user_loads_session_event"
    description = "The user wants to load a previous session."
    session_id: str
    full_events_history: List[AbstractEvent]

class UserLoadsSession(AbstractAction):
    trigger_event_class = UserLoadsSessionEvent
    description = "The user wants to load a previous session."

    def __init__(self, host_object: AbstractObject):
        super().__init__(host_object=host_object)

    def __call__(self, event: UserStartsNewSessionEvent):
        # loads the session from the session_id
        # that means
        # loading the state and memories of every agent and object
        # sending all the event history to the front
        pass
