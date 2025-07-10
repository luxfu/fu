class BusinessException(Exception):
    def __init__(self, code: int, message: str, data: dict = None):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(message)

# 特定业务异常


class NotFoundException(BusinessException):
    def __init__(self, resource: str, id: int):
        super().__init__(
            code=404,
            message=f"{resource} 不存在",
            data={"resource": resource, "id": id}
        )
