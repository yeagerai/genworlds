from yeager_core.worlds.base_world import BaseObject


def read_jobs(agent_name):
    agent_jobs = []
    for job_name, job in blackboard.data.items():
        if job["assigned_to"] == agent_name:
            agent_jobs.append({job_name: job})
    return agent_jobs


def update_job(agent_name, job_name, job):
    if (
        blackboard.data.get(job_name)
        and blackboard.data[job_name]["assigned_to"] == agent_name
    ):
        blackboard.data[job_name] = job
    else:
        raise ValueError(
            f"Job '{job_name}' not found or not assigned to agent '{agent_name}'"
        )


def add_job(job_name, job_data):
    if job_name in blackboard.data:
        raise ValueError(f"Job '{job_name}' already exists.")
    blackboard.data[job_name] = job_data


def delete_job(agent_name, job_name):
    if (
        job_name in blackboard.data
        and blackboard.data[job_name]["assigned_to"] == agent_name
    ):
        del blackboard.data[job_name]
    else:
        raise ValueError(
            f"Job '{job_name}' not found or not assigned to agent '{agent_name}'"
        )


blackboard = BaseObject(
    name="blackboard",
    description="The blackboard is a place where agents can read and write all the jobs they have to do while in the lab",
    interactions={
        "read": read_jobs,
        "update": update_job,
        "add": add_job,
        "delete": delete_job,
    },
    data={
        "job1": {
            "description": "Find a way to make the world a better place",
            "assigned_to": "agent1",
            "output_format": "json",
            "status": "to be done",
        },
        "job2": {
            # Add properties for job2 as needed
        },
    },
)
