from pydantic import BaseModel

class CreateTaskSchema(BaseModel):
    topic: str
    description: str
    agent_id: str
    expected_output: str