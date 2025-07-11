from pydantic import BaseModel, Field, ValidationError
from typing import Callable, TypeVar, Optional, Generic
from functools import wraps
from ninja import NinjaAPI
from django.http import JsonResponse
T = TypeVar('T')


class BaseResponse(BaseModel, Generic[T]):
    code: int = Field(200, description="状态码")
    message: str = Field("success", description="消息描述")
    data: Optional[T] = Field(None, description="响应数据")

    @classmethod
    def success(cls, data: T = None, message: str = "操作成功"):
        return cls(code=200, message=message, data=data)

    @classmethod
    def error(cls, code: int, message: str, data: dict = None):
        return cls(code=code, message=message, data=data)


class PaginatedResponse(BaseResponse, Generic[T]):
    total: int = Field(..., description="总记录数")  # Field(...)特殊用法，表示必须且没有默认值
    page: int = Field(1, description="当前页码")
    page_size: int = Field(10, description="每页数量")

    @classmethod
    def paginated(
        cls,
        queryset: list,
        page: int = 1,
        page_size: int = 10,
        message: str = "查询成功"
    ):
        total = queryset.count()
        items = queryset[(page-1)*page_size:page*page_size]
        return cls(
            code=200,
            message=message,
            data=items,
            total=total,
            page=page,
            page_size=page_size
        )


class ErrorDetail(BaseModel):
    field: str = Field(..., description="错误字段")
    message: str = Field(..., description="错误信息")
    code: str = Field(..., description="错误代码")


class ErrorResponse(BaseResponse):
    # errors: Optional[list[ErrorDetail]] = Field(None, description="错误详情列表")
    errors: Optional[T] = Field(None, description="错误详情列表")

    def to_http_response(self, api: NinjaAPI = None):
        """将错误响应转换为 Django HttpResponse"""
        response_data = self.model_dump()
        if api:
            # 使用 NinjaAPI 的响应包装
            return api.create_response(
                request=None,  # 不需要实际请求对象
                data=response_data,
                status=self.code
            )
        else:
            # 直接创建 JsonResponse
            return JsonResponse(response_data, status=self.code)

    @classmethod
    def error(cls, code: int, message: str, errors: dict = None):
        return cls(code=code, message=message, errors=errors)

    @classmethod
    def validation_error(cls, errors: list):
        """创建验证错误响应"""
        error_details = []
        for error in errors:
            # 处理两种来源的错误格式
            if isinstance(error, dict):
                # Django Ninja 格式错误
                loc = error.get("loc", [])
                msg = error.get("msg", "Invalid input")
                error_type = error.get("type", "validation_error")
            else:
                # Pydantic 格式错误
                loc = getattr(error, "loc", [])
                msg = getattr(error, "msg", "Invalid input")
                error_type = getattr(error, "type", "validation_error")

            error_details.append(ErrorDetail(
                field="->".join(map(str, loc)),
                message=msg,
                code=error_type
            ))

        return cls(
            code=422,
            message="数据验证失败",
            errors={"detail": error_details}
        )


def standard_response(view_func: Callable):
    """非baseresponse类标准化"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        try:
            result = view_func(request, *args, **kwargs)
            # 如果视图返回 BaseResponse 实例，直接返回
            if isinstance(result, BaseResponse):
                return result
            # 处理普通响应
            status = 200
            if isinstance(result, tuple) and len(result) == 2:
                data, status = result
            else:
                data = result

            return BaseResponse.success(data=data)

        except ValidationError as e:
            return ErrorResponse.validation_error(e.errors())

        except Exception as e:
            # 其他异常处理
            return ErrorResponse.error(
                code=500,
                message="服务器内部错误",
                errors={"detail": str(e)}
            )

    return wrapper
