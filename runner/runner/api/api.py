
# api.py
from .v1 import router as v1_router
from ninja import NinjaAPI
from pydantic import ValidationError as PydanticValidationErr
from ninja.errors import ValidationError as NinjaValidationErr
from runner.api.response import ErrorResponse
from runner.api.exceptions import BusinessException
api = NinjaAPI()


@api.exception_handler(BusinessException)
def handle_business_exception(request, exc: BusinessException):
    return ErrorResponse.error(
        code=exc.code,
        message=exc.message,
        data=exc.data
    )


@api.exception_handler(NinjaValidationErr)
@api.exception_handler(PydanticValidationErr)
def handle_validation_error(request, exc):
    # 获取错误列表
    if hasattr(exc, 'errors'):
        errors = exc.errors  # Django Ninja 的错误格式
    elif hasattr(exc, 'errors') and callable(exc.errors):
        errors = exc.errors()  # Pydantic v2 的错误格式
    else:
        errors = []

    # 使用 ErrorResponse 创建标准错误响应
    return api.create_response(
        request,
        ErrorResponse.validation_error(errors).model_dump(),
        status=422
    )


@api.exception_handler(Exception)
def handle_generic_exception(request, exc: Exception):
    import traceback
    traceback.print_exc()  # 日志记录

    return ErrorResponse.error(
        code=500,
        message="服务器内部错误",
        data={"detail": str(exc)}
    )


api.add_router("/v1/", v1_router)
