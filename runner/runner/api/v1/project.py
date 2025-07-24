from ninja import Schema, Router
from pydantic import field_validator
from runner.models import Project
from datetime import datetime
from runner.api.response import BaseResponse, PaginatedResponse
from typing import Optional
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


@router.post("", response=BaseResponse[PorjectOut])
def create_project(request, payload: ProjectIn):
    project = Project.objects.create(**payload.dict())
    return BaseResponse.succeed(data=project)


@router.put("/{id}", response=BaseResponse[PorjectOut])
def edit_project(request, id: int, data: ProjectIn):
    project = Project.objects.get(id=id)
    dict_data = data.dict()
    for attr, value in dict_data.items():
        setattr(project, attr, value)
    project.save()
    return BaseResponse.succeed(data=project)


@router.delete("/{id}")
def delete_project(request, id: int):
    project = Project.objects.get(id=id).delete()
    return BaseResponse.succeed()


@router.get("", response=PaginatedResponse[PorjectOut])
def list_project(request, page: int, pageSize: int):
    project = Project.objects.all()
    return PaginatedResponse.paginated(queryset=project, page_size=pageSize, page=page)
