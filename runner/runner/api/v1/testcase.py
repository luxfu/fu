from ninja import ModelSchema, Router, Field, Schema
from ninja.orm import create_schema
from runner.models import TestCase
from runner.api.response import BaseResponse, PaginatedResponse
from typing import Optional, Union
router = Router(tags=['测试用例'])

BaseCaseOut = create_schema(TestCase)


class CaseOut(BaseCaseOut):
    action_type: str = Field(None, alias='action')


class CaseIn(Schema):
    url: str | None
    url_override: int = 0
    custom_locator: str | None
    custom_locator_type: str | None
    action_type: str | None
    action_value: str | None
    assert_type: str | None
    assert_expression: str | None
    order: int
    po_id: int | None


@router.post("", response=BaseResponse[CaseIn])
def create_case(request, payload: CaseIn):
    case = TestCase.objects.create(**payload.dict())
    return BaseResponse.succeed(data=case)


@router.get("", response=PaginatedResponse[CaseOut])
def list_case(request, page: int = 1, pageSize: int = 10):
    cases = TestCase.objects.all()
    return PaginatedResponse.paginated(queryset=cases, page=page, page_size=pageSize)
