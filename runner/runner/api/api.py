
# api.py
from .v1 import router as v1_router
from ninja import NinjaAPI
from pydantic import ValidationError
api = NinjaAPI()


@api.exception_handler(ValidationError)
def handle_validation_error(request, exc):
    print(111111111111111)
    return api.create_response(
        request,
        {"error": "Validation failed", "details": exc.errors()},
        status=422
    )


api.add_router("/v1/", v1_router)
