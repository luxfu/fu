from ninja import Router, Schema, Field
from ninja.orm import create_schema
from pydantic import field_validator
from runner.models import Tasks, TestSuite
from runner.api.response import BaseResponse, PaginatedResponse
from core.tasks import run_test_suite
from datetime import datetime
router = Router(tags=["任务"])

BaseTasksOut = create_schema(Tasks)


class TasksOut(BaseTasksOut):
    start_time: str
    end_time: str

    @field_validator("start_time", mode="before")
    def format_start_time(cls, v: datetime):
        return v.strftime("%Y-%m-%d %H:%M:%S") if isinstance(v,
                                                             datetime) else v

    @field_validator("end_time", mode="before")
    def format_end_time(cls, v: datetime):
        return v.strftime("%Y-%m-%d %H:%M:%S") if isinstance(v,
                                                             datetime) else v


class TasksIn(Schema):
    task_name: str = Field(..., alias="name")
    executor: str
    suite_id: int


@router.post("", response=BaseResponse[TasksOut])
def create_task(request, payload: TasksIn):
    task_dict = payload.model_dump(exclude={"suite_id"})
    suite = TestSuite.objects.filter(id=payload.suite_id).first()
    task = Tasks.objects.create(test_suite=suite, **task_dict)
    return BaseResponse.succeed(data=task)


@router.get("", response=PaginatedResponse[TasksOut])
def list_task(request, page: int, pageSize: int):
    task = Tasks.objects.all()
    return PaginatedResponse.paginated(queryset=task, page=page, page_size=pageSize)


@router.post("run", response=BaseResponse[TasksOut])
def run_task(request, task_id: int):
    run_test_suite(task_id)
    task = Tasks.objects.get(id=task_id)
    return BaseResponse.succeed(data=task)
