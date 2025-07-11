
# api.py
from ninja.errors import HttpError
from .v1 import router as v1_router
from ninja import NinjaAPI
from pydantic import ValidationError as PydanticValidationErr
from ninja.errors import ValidationError as NinjaValidationErr
from runner.api.response import ErrorResponse
from runner.api.exceptions import BusinessException

api = NinjaAPI()


@api.exception_handler(HttpError)
def handle_http_error(request, exc):
    """处理所有 Django Ninja 的 HTTP 错误"""
    if "Cannot parse request body" in str(exc):
        # 专门处理 JSON 解析错误
        return ErrorResponse.error(code=400, message="请求体解析失败", errors={"detail": str(exc)}).to_http_response()
    # 其他http错误
    return ErrorResponse.error(code=exc.code, message="请求处理失败", errors={"detail": str(exc)}).to_http_response()


@api.exception_handler(BusinessException)
def handle_business_exception(request, exc: BusinessException):
    return ErrorResponse.error(
        code=exc.code,
        message=exc.message,
        errors=exc.data
    ).to_http_response(api)


@api.exception_handler(PydanticValidationErr)
@api.exception_handler(NinjaValidationErr)
def handle_validation_error(request, exc):
    # 获取错误列表
    if hasattr(exc, 'errors'):
        errors = exc.errors  # Django Ninja 的错误格式
    elif hasattr(exc, 'errors') and callable(exc.errors):
        errors = exc.errors()  # Pydantic v2 的错误格式
    else:
        errors = []

    # 使用 ErrorResponse 创建标准错误响应
    return ErrorResponse.validation_error(errors).to_http_response(api)


@api.exception_handler(Exception)
def handle_generic_exception(request, exc: Exception):
    import traceback
    traceback.print_exc()  # 控制台或日志文件输出错误记录

    return api.create_response(
        request,
        ErrorResponse.error(
            code=500,
            message="服务器内部错误",
            errors={"detail": str(exc)}
        ),
        status=500
    )


api.add_router("/v1/", v1_router)
