from yeager_core.environments.base_environment import BaseEnvironment
from .env_agents.y_tools import ytools
from .env_objects.blackboard import blackboard

agents_creator_lab = BaseEnvironment(
    name="agents_creator_lab",
    description="This is a lab where agents can be created",
    objects=[blackboard],
    agents=[ytools],
)

agents_creator_lab.run()
