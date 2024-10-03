from fastapi import APIRouter
from fastapi.responses import JSONResponse
from src.agents.controllers import get_agents_ctrl
from src.tasks.serializers import CreateTaskSchema
from src.tasks.controllers import get_tasks_ctrl, create_tasks_ctrl, update_task_ctrl
from src.crew_search_bot import CrewAgent

router = APIRouter()


@router.get("")
def get_task(id: int):
    tasks = get_tasks_ctrl(id)

    return JSONResponse(
        content={
            "id": tasks.id,
            "description": tasks.description,
            "agent_id": tasks.agent_id,
            "created_at": str(tasks.created_at),
        }
    )


@router.post("")
def create_task(tasks: CreateTaskSchema):
    new_task = create_tasks_ctrl(tasks)

    agent = get_agents_ctrl(tasks.agent_id)
    agent = agent[0]

    init_task = CrewAgent(
        role=agent["role"],
        backstory=agent["backstory"],
        goal=agent["goal"],
        expected_output=new_task.expected_output,
    )
    prompt = f"""Here is the goal of the task: {agent['goal']}. Follow the instruction: {tasks.description}. Optimize the task by ensuring clarity, precision, and accuracy in the information gathered, while maintaining alignment with the specified goal. Focus on delivering concise insights that meet the task requirements effectively."""
    # res = init_task.main(description=tasks.description)
    res = init_task.main(description=prompt)
    breakpoint()
    final_res = res.raw

    update_task_ctrl(new_task.id, res)
    return JSONResponse(
        content={
            "id": new_task.id,
            "description": new_task.description,
            "agent_id": new_task.agent_id,
            "expected_output": new_task.expected_output,
            "response": final_res,
        }
    )
