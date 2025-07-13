from ninja import Router, Schema
from ninja.orm import create_schema
from runner.models import TestSuite, SuiteCaseRelation, TestCase
from runner.api.response import BaseResponse, standard_response
from typing import Optional
from pydantic import field_validator
from django.db import transaction
router = Router(
    tags=["测试套件suite"]
)


class TestSuiteIn(Schema):
    name: str
    environment: Optional[str] = None
    status: Optional[str] = "draft"
    case_id: list[int]

    @field_validator("case_id", mode="before")
    def validate_case_id(cls, v):
        return v


TestSuiteOut = create_schema(TestSuite)


@router.post("/testsuite", response=BaseResponse[TestSuiteOut])
def create_testsuite(request, payload: TestSuiteIn):
    suite = payload.model_dump(exclude={"case_id"})
    with transaction.atomic():
        test_suite = TestSuite.objects.create(**suite)
        test_cases = TestCase.objects.filter(id__in=payload.case_id)
        relations = [
            SuiteCaseRelation(
                test_suite=test_suite,
                test_case=case,
                order=i+1
            ) for i, case in enumerate(test_cases)
        ]
        SuiteCaseRelation.objects.bulk_create(relations)
    return BaseResponse.success(data=test_suite)
