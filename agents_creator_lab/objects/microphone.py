from typing import List
from yeager_core.events.websocket_event_handler import Event

from yeager_core.worlds.base_world import BaseObject
from yeager_core.objects.base_object import BaseObject





class AgentSpeaksIntoMicrophone(Event):
    event_type = "agent_speaks_into_microphone"
    description = "The holder of the microphone speaks into the microphone."
    message: str

# class AgentSpeaksIntoMicrophoneAndHandsItOver(Event):
#     event_type = "agent_speaks_into_microphone_and_hands_it_over"
#     description = "The holder of the microphone speaks into the microphone, and gives it to someone else."
#     message: str
#     recipient_id: str

# class HostTakesBackTheMicrophone(Event):
#     event_type = "host_takes_back_the_microphone"
#     description = "The host forcibly takes back the microphone."


class Microphone(BaseObject):
    host: str

    def __init__(
        self,
        name: str,
        description: str,
        host: str,
        id: str = None,
    ):
        super().__init__(
            name,
            description,
            id=id,
        )

        self.host = host
        self.holder = host

        self.register_event_listeners([
            # (AgentRequestsMicrophoneState, self.agent_requests_microphone_state),
            (AgentSpeaksIntoMicrophone, self.agent_speaks_into_microphone_listener),
            # (AgentSpeaksIntoMicrophoneAndHandsItOver, self.agent_speaks_into_microphone_and_hands_it_over_listener),
            # (HostTakesBackTheMicrophone, self.host_takes_back_the_microphone_listener),
        ])    


    # def agent_requests_microphone_state(self, event: AgentRequestsMicrophoneState):
    #     print(f"Agent {event.sender_id} requests information about the microphone.")
    #     self.send_event(MicrophoneSendsState,
    #         host=self.host,
    #         holder=self.holder,
    #     )


    def agent_speaks_into_microphone_listener(self, event: AgentSpeaksIntoMicrophone):
        if (event.sender_id != self.holder):
            print(f"Agent {event.sender_id} is not the holder of the microphone.")
            return
        print(f"Agent {event.sender_id} says: {event.message}.")

    # def agent_speaks_into_microphone_and_hands_it_over_listener(self, event: AgentSpeaksIntoMicrophone):
    #     if (event.sender_id != self.holder):
    #         print(f"Agent {event.sender_id} is not the holder of the microphone.")
    #         return
    #     print(f"Agent {event.sender_id} says: {event.message}.")
    #     self.holder = event.recipient_id
    #     print(f"Agent {event.sender_id} hands the microphone over to agent {event.recipient_id}.")
    #     self.send_event(MicrophoneSendsState,
    #         host=self.host,
    #         holder=self.holder,
    #     )

    # def host_takes_back_the_microphone_listener(self, event: HostTakesBackTheMicrophone):
    #     if (event.sender_id != self.host):
    #         print(f"Agent {event.sender_id} is not the host.")
    #         return
    #     print(f"Host {event.sender_id} takes back the microphone.")
    #     self.holder = self.host
    #     self.send_event(MicrophoneSendsState,
    #         host=self.host,
    #         holder=self.holder,
    #     )



    