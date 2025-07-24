from ninja import Schema, Router
from ninja.orm import create_schema
from runner.models import PageObject
from typing import Optional, Union
from pydantic import model_validator, field_validator
from runner.api.exceptions import BusinessException
from datetime import datetime
from runner.api.response import BaseResponse, standard_response, PaginatedResponse
from pydantic import BaseModel
router = Router(tags=["po对象"])


BasePageObjectOut = create_schema(PageObject)


class PageObjectOut(BasePageObjectOut):
    created_at: str

    @field_validator("created_at", mode="before")
    def format_create_at(cls, v: datetime):
        return v.strftime("%Y-%m-%d %H:%M:%S") if isinstance(v, datetime) else v


class PageObjectIn(Schema):
    po_id: int
    name: str
    locator: Union[str, None] = ""
    locator_type: Optional[str] = ""
    url: Optional[str] = ""
    is_relative: Optional[bool] = False

    @model_validator(mode="after")
    def validator_url_or_locator(self):
        if not self.url:
            if not self.locator and not self.locator_type:
                raise BusinessException(code=422, message="数据验证失败", data={
                                        "details": "url和locator必须选择一种"})
                # raise ValueError("url和locator必须选择一种")
        return self


@router.post("", response=BaseResponse[PageObjectOut])
def create_po(request, payload: PageObjectIn):
    po = PageObject.objects.create(**payload.dict())
    return BaseResponse.succeed(data=po, message="创建成功")


@router.put("/{id}", response=BaseResponse[PageObjectOut])
def edit_po(request, id: int, payload: PageObjectIn):
    po = PageObject.objects.get(id=id)
    dict_data = payload.dict()
    for attr, value in dict_data.items():
        setattr(po, attr, value)
    po.save()
    return BaseResponse.succeed(data=po)


@router.delete("/{id}")
def delete_po(request, id: int):
    PageObject.objects.get(id=id).delete()
    return BaseResponse.succeed()


@router.get("", response=PaginatedResponse[PageObjectOut])
def list_pageobjects(request, page: int, pageSize: int):
    po = PageObject.objects.all()
    return PaginatedResponse.paginated(queryset=po, page_size=pageSize, page=page)
