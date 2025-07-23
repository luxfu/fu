from ninja import Router, Schema, Field
from ninja.orm import create_schema
from runner.models import Tasks, TestSuite
from runner.api.response import BaseResponse
from core.tasks import run_test_suite
router = Router(tags=["任务"])

TasksOut = create_schema(Tasks)


class TasksIn(Schema):
    task_name: str = Field(..., alias="name")
    executor: str
    suite_id: int


@router.post("/task", response=BaseResponse[TasksOut])
def create_task(request, payload: TasksIn):
    task_dict = payload.model_dump(exclude={"suite_id"})
    suite = TestSuite.objects.filter(id=payload.suite_id).first()
    task = Tasks.objects.create(test_suite=suite, **task_dict)
    return BaseResponse.succeed(data=task)


@router.post("/task/run", response=BaseResponse[TasksOut])
def run_task(request, task_id: int):
    run_test_suite(task_id)
    task = Tasks.objects.get(id=task_id)
    return BaseResponse.succeed(data=task)
