from .project import router as project_router
from .pageobject import router as po_router
from .testsuite import router as suite_router
from .tasks import router as task_router
from .testcase import router as case_router
from ninja import Router
from ninja.security import HttpBearer


class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        if token == "SECRET_TOKEN":
            return token  # 返回非None即认证通过
        return None


# router = Router(auth=AuthBearer())
router = Router()
router.add_router("/project", project_router)
router.add_router("/pageobject", po_router)
router.add_router("/suite", suite_router)
router.add_router("/task", task_router)
router.add_router("/case", case_router)
