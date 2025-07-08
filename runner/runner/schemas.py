from ninja import Schema
from ninja.orm import create_schema
from .models import Project
from pydantic import field_validator
from datetime import datetime

BaseProjectSchema = create_schema(
    Project, fields=["id", "name", "status", "create_time"])


class ProjectSchema(BaseProjectSchema):
    create_time: str

    @field_validator("create_time", mode="before")
    def format_create_time(cls, v):
        if isinstance(v, datetime):
            return v.strftime("%Y-%m-%d %H:%M:%S")
        return v


class ProjectCreate(Schema):
    name: str
    status: int
