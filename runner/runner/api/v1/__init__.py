from .project import router as project_router
from .pageobject import router as po_router
from ninja import Router
from ninja.security import HttpBearer


class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        if token == "SECRET_TOKEN":
            return token  # 返回非None即认证通过
        return None


# router = Router(auth=AuthBearer())
router = Router()
router.add_router("/", project_router)
router.add_router("/", po_router)
