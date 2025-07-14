import os
import json
import shutil
import subprocess
from datetime import datetime
from django.conf import settings
from allure_commons.types import AttachmentType
from allure_commons.model2 import TestResult, TestStepResult, Status
from allure_commons.model2 import Label, Link, Parameter
from allure_commons.utils import uuid4
from utils.logger import setup_logger

logger = setup_logger(__name__)


class AllureReportGenerator:
    def __init__(self, execution_id):
        self.execution_id = execution_id
        self.report_dir = self._get_report_dir()
        self.results_dir = os.path.join(self.report_dir, "results")
        self.report_data = {
            "test_cases": [],
            "start_time": datetime.utcnow().isoformat(),
            "stop_time": None,
            "status": "passed",
            "statistics": {
                "passed": 0,
                "failed": 0,
                "broken": 0,
                "skipped": 0,
                "total": 0
            }
        }
        os.makedirs(self.results_dir, exist_ok=True)

    def _get_report_dir(self):
        base_dir = settings.REPORTS_ROOT
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(base_dir, f"execution_{self.execution_id}_{timestamp}")

    def create_test_case(self, name, description="", suite="Default Suite", tags=None):
        test_case = {
            "uuid": str(uuid4()),
            "name": name,
            "fullName": f"{suite}.{name}",
            "labels": [
                Label(name="suite", value=suite),
                Label(name="framework", value="django-selenium")
            ],
            "links": [],
            "parameters": [],
            "steps": [],
            "attachments": [],
            "status": Status.PASSED,
            "statusDetails": None,
            "description": description,
            "start": datetime.utcnow().isoformat(),
            "stop": None,
            "historyId": str(uuid4())
        }

        if tags:
            for tag in tags:
                test_case["labels"].append(Label(name="tag", value=tag))

        self.report_data["test_cases"].append(test_case)
        self.report_data["statistics"]["total"] += 1
        return test_case

    def add_step(self, test_case, name, status=Status.PASSED, attachments=None):
        step = TestStepResult(
            name=name,
            status=status,
            start=datetime.utcnow().isoformat(),
            stop=datetime.utcnow().isoformat(),
            attachments=attachments or []
        )
        test_case["steps"].append(step)

        # 更新测试用例状态
        if status in [Status.FAILED, Status.BROKEN] and test_case["status"] == Status.PASSED:
            test_case["status"] = status
            self._update_statistics(status)

        return step

    def add_attachment(self, step, name, content, attachment_type=AttachmentType.TEXT):
        attachment_uuid = str(uuid4())
        attachment_filename = f"{attachment_uuid}-attachment{attachment_type.extension}"
        attachment_path = os.path.join(self.results_dir, attachment_filename)

        # 保存附件内容
        if isinstance(content, str):
            with open(attachment_path, "w", encoding="utf-8") as f:
                f.write(content)
        elif isinstance(content, bytes):
            with open(attachment_path, "wb") as f:
                f.write(content)
        else:
            logger.warning(
                f"Unsupported attachment content type: {type(content)}")
            return None

        # 创建附件对象
        attachment = {
            "name": name,
            "source": attachment_filename,
            "type": attachment_type.value
        }

        step.attachments.append(attachment)
        return attachment

    def add_screenshot(self, step, driver, name="Screenshot"):
        if hasattr(driver, "get_screenshot_as_png"):
            screenshot = driver.get_screenshot_as_png()
            return self.add_attachment(step, name, screenshot, AttachmentType.PNG)
        return None

    def finalize_test_case(self, test_case):
        test_case["stop"] = datetime.utcnow().isoformat()

        # 保存测试用例结果文件
        test_result = TestResult(**test_case)
        result_file = os.path.join(
            self.results_dir, f"{test_case['uuid']}-result.json")

        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(test_result.to_dict(), f, ensure_ascii=False, indent=2)

    def finalize_report(self):
        self.report_data["stop_time"] = datetime.utcnow().isoformat()

        # 生成Allure报告
        report_cmd = [
            "allure", "generate",
            self.results_dir,
            "-o", self.report_dir,
            "--clean"
        ]

        try:
            subprocess.run(report_cmd, check=True)
            logger.info(f"Allure report generated at: {self.report_dir}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to generate Allure report: {e}")
            return None

        # 压缩报告（可选）
        if settings.COMPRESS_REPORTS:
            self._compress_report()

        return os.path.join(self.report_dir, "index.html")

    def _update_statistics(self, status):
        status_str = status.value.lower()
        if status_str in self.report_data["statistics"]:
            self.report_data["statistics"][status_str] += 1

        # 更新整体执行状态
        if status in [Status.FAILED, Status.BROKEN]:
            self.report_data["status"] = "failed"

    def _compress_report(self):
        shutil.make_archive(self.report_dir, 'zip', self.report_dir)
        return f"{self.report_dir}.zip"
