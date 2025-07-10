from ninja import Schema, Router
from pydantic import field_validator
from runner.models import Project
from datetime import datetime

router = Router(tags=["项目"])


class PorjectOut(Schema):
    id: int
    name: str
    status: int
    create_time: str

    @field_validator("create_time", mode="before")
    def format_create_time(cls, v: datetime):
        return v.strftime("%Y-%m-%d %H:%M:%S") if isinstance(v,
                                                             datetime) else v

    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S")  # 自定义时间格式
        }


class ProjectIn(Schema):
    name: str
    status: int = 0

    class Config:
        model = Project


@router.post("/", response=PorjectOut)
def create_project(request, payload: ProjectIn):
    project = Project.objects.create(**payload.dict())
    return project
