from yeager_core.environments.base_environment import BaseObject

def read_jobs(agent_name):
    agent_jobs = []
    for job in blackboard.data:
        if job["assigned_to"] == agent_name:
            agent_jobs.append(job)
    return agent_jobs


blackboard = BaseObject(
    name="blackboard",
    description="The blackboard is a place where agents can write down their thoughts and ideas",
    interactions={
        "read": read_jobs,
        "write": lambda: print("Writing on the blackboard"),
    },
    data={
        "job1": {
            "description": "Find a way to make the world a better place",
            "assigned_to": "agent1",
            "output_format": "json",
            "status": "to be done",
        },
        "job2": {},
    },
)
