from pydantic import BaseModel


class Job(BaseModel):
    id: str
    description: str
    assigned_to: str
    output_format: str
    status: str
    # creation_date: 
    # end_date:
    # job_dependencies:
