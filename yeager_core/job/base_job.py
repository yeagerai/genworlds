from typing import Callable
'''
I want you to do XXXXXXXXXXXXXXx 
output_format: "json"
testing_function: "load_memory"
expected_value: "? if applies, otherwise will be load and execute and then ask for yes or no feedback"
'''
class Job:
    task_prompt: str
    output_format: str
    testing_function: Callable
    expected_value: str
    assigned_to: str
    priority: int
    status: str