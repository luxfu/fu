import os
import json
import traceback
import subprocess
import uuid
import time
from typing import Dict, List, Optional
from allure_commons.types import AttachmentType
from allure_commons.model2 import Status
from django.conf import settings

logger = settings.LOGGER(__name__)


class AllureReportGenerator:
    def __init__(self, execution_id: str):
        self.execution_id = execution_id
        self.base_dir = self._get_base_dir()
        self.report_dir = os.path.join(self.base_dir, "reports")
        self.results_dir = os.path.join(self.base_dir, "results")
        self.attachments_dir = os.path.join(self.results_dir, "attachments")
        self.status = 'passed'  # 只是为了判断整体是否成功，有一个step失败都算失败
        # 创建目录
        os.makedirs(self.results_dir, exist_ok=True)
        os.makedirs(self.attachments_dir, exist_ok=True)

        # 存储测试用例和容器
        self.test_cases: Dict[str, dict] = {}
        self.containers: Dict[str, dict] = {}

        # 按套件分组存储测试用例UUID
        self.suite_children: Dict[str, List[str]] = {}

        # 记录开始时间（毫秒时间戳）
        self.start_time = int(time.time() * 1000)

    def _get_base_dir(self) -> str:
        """生成报告目录路径"""
        base_dir = settings.REPORTS_ROOT
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        return os.path.join(base_dir, f"{self.execution_id}_{timestamp}")

    def create_test_case(self, name: str, full_name: str, suite: str,
                         description: str = "", tags: Optional[List[str]] = None,
                         links: Optional[List[Dict]] = None, epic: Optional[str] = None,
                         feature: Optional[str] = None, story: Optional[str] = None,
                         severity: Optional[str] = None) -> dict:
        """创建测试用例"""
        test_uuid = str(uuid.uuid4())

        # 构建测试用例的基本结构
        test_case = {
            "name": name,
            "status": Status.PASSED,  # 直接使用Status枚举值
            "statusDetail": {},
            "description": description,
            "steps": [],
            "start": self.start_time,
            "stop": None,
            "uuid": test_uuid,
            "historyId": str(uuid.uuid4()),
            "testCaseId": str(uuid.uuid4()),
            "fullName": full_name,
            "labels": [
                {"name": "suite", "value": suite},
                {"name": "framework", "value": "django-selenium"}
            ],
            "links": links or []
        }

        # 添加标签
        if tags:
            for tag in tags:
                test_case["labels"].append({"name": "tag", "value": tag})
        if epic:
            test_case["labels"].append({"name": "epic", "value": epic})
        if feature:
            test_case["labels"].append({"name": "feature", "value": feature})
        if story:
            test_case["labels"].append({"name": "story", "value": story})
        if severity:
            test_case["labels"].append({"name": "severity", "value": severity})

        # 存储测试用例
        self.test_cases[test_uuid] = test_case

        # 按套件分组
        if suite not in self.suite_children:
            self.suite_children[suite] = []
        self.suite_children[suite].append(test_uuid)

        return test_case

    def add_step(self, test_case: dict, name: str, status: Status = Status.PASSED, exception: Optional[Exception] = None) -> dict:
        """添加步骤到测试用例"""
        step = {
            "name": name,
            "status": status,  # 直接使用Status枚举值
            "start": int(time.time() * 1000),
            "stop": int(time.time() * 1000),
            "attachments": []
        }
        # 如果步骤失败且有异常，添加statusDetails
        if status in [Status.FAILED, Status.BROKEN] and exception:
            step["statusDetails"] = self._create_status_details(exception)
            test_case["steps"].append(step)
            self.status = 'failed'

        # 更新测试用例状态：如果步骤失败且当前用例状态是通过，则更新状态
        if status != Status.PASSED and test_case["status"] == Status.PASSED:
            test_case["status"] = status

        return step

    def _create_status_details(self, exception: Exception) -> dict:
        """创建状态详情信息"""
        # 获取异常类型和消息
        exc_type = type(exception).__name__
        exc_message = str(exception)

        # 获取堆栈跟踪
        exc_traceback = traceback.format_exc()

        return {
            "message": f"{exc_type}: {exc_message}",
            "trace": exc_traceback
        }

    def add_attachment(self, step: dict, name: str, content: bytes, attachment_type: AttachmentType) -> str:
        """添加附件到步骤"""
        attachment_uuid = str(uuid.uuid4())
        extension = attachment_type.extension
        filename = f"{attachment_uuid}-attachment.{extension}"
        filepath = os.path.join(self.attachments_dir, filename)

        # 保存附件内容 - 根据内容类型决定写入方式
        if isinstance(content, str):
            # 字符串内容使用文本模式写入
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
        else:
            # 字节内容使用二进制模式写入
            with open(filepath, "wb") as f:
                f.write(content)

        # 记录附件信息
        attachment = {
            "name": name,
            "source": f"attachments/{filename}",
            "type": attachment_type.value[0]  # 取MIME类型，例如'image/png'
        }
        step["attachments"].append(attachment)
        return filepath

    def add_screenshot(self, step: dict, driver, name: str = "Screenshot") -> Optional[str]:
        """添加Selenium截图到步骤"""
        try:
            if hasattr(driver, "get_screenshot_as_png"):
                screenshot = driver.get_screenshot_as_png()
                return self.add_attachment(step, name, screenshot, AttachmentType.PNG)
            return None
        except Exception as e:
            logger.error(f"截图失败: {e}")
            return None

    def finalize_test_case(self, test_case: dict, exception: Optional[Exception] = None):
        """结束测试用例：设置停止时间并保存为result.json文件"""
        if test_case.get("stop") is None:
            test_case["stop"] = int(time.time() * 1000)

        # 如果测试用例失败且有异常，添加statusDetails
        if test_case["status"] in [Status.FAILED, Status.BROKEN] and exception:
            if "statusDetails" not in test_case:
                test_case["statusDetails"] = self._create_status_details(
                    exception)

        # 保存为result.json文件
        result_file = os.path.join(
            self.results_dir, f"{test_case['uuid']}-result.json")
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(test_case, f, ensure_ascii=False, indent=2)
        logger.debug(f"保存测试用例结果: {result_file}")

    def _create_categories_file(self):
        """创建categories.json文件解决root节点empty问题"""
        categories = [
            {
                "name": "Ignored tests",
                "matchedStatuses": ["skipped"]
            },
            {
                "name": "Infrastructure problems",
                "matchedStatuses": ["broken", "failed"],
                "messageRegex": ".*bye-bye.*"
            },
            {
                "name": "Outdated tests",
                "matchedStatuses": ["broken"],
                "traceRegex": ".*FileNotFoundException.*"
            },
            {
                "name": "Product defects",
                "matchedStatuses": ["failed"]
            },
            {
                "name": "Test defects",
                "matchedStatuses": ["broken"]
            }
        ]

        categories_file = os.path.join(self.results_dir, "categories.json")
        with open(categories_file, "w", encoding="utf-8") as f:
            json.dump(categories, f, ensure_ascii=False, indent=2)
        logger.debug(f"创建分类文件: {categories_file}")

    def generate_container_files(self):
        """生成所有容器文件"""
        # 为每个测试套件创建容器
        for suite, children in self.suite_children.items():
            container_uuid = str(uuid.uuid4())
            container = {
                "uuid": container_uuid,
                "name": f"{suite} Suite",  # 添加容器名称
                "children": children,
                "befores": [{
                    "name": f"{suite}",
                    "status": Status.PASSED,
                    "start": self.start_time,
                    "stop": self.start_time
                }],
                "afters": [],
                "start": self.start_time,
                "stop": int(time.time() * 1000)
            }
            self.containers[container_uuid] = container

        # 保存所有容器文件
        for container_uuid, container_data in self.containers.items():
            container_file = os.path.join(
                self.results_dir, f"{container_uuid}-container.json")
            with open(container_file, "w", encoding="utf-8") as f:
                json.dump(container_data, f, ensure_ascii=False, indent=2)
            logger.debug(f"创建容器文件: {container_file}")

    def generate_report(self):
        """生成完整的Allure报告"""
        # 1. 完成所有测试用例
        for test_case in self.test_cases.values():
            self.finalize_test_case(test_case)

        # 2. 生成容器文件
        self.generate_container_files()

        # 3. 创建分类文件
        self._create_categories_file()

        # 4. 确保所有文件都已写入
        logger.info(f"结果目录内容: {os.listdir(self.results_dir)}")

        # 5. 生成Allure报告
        report_cmd = [
            "allure", "generate", self.results_dir,
            "-o", self.report_dir, "--clean"
        ]
        logger.info(f"执行报告生成命令: {' '.join(report_cmd)}")
        try:
            # 添加详细的日志记录
            result = subprocess.run(
                report_cmd,
                shell=True,
                check=True
            )
            logger.info(f"报告生成成功: {self.report_dir}")
            logger.debug(f"Allure输出: {result.stdout}")

            # 检查报告文件是否存在
            report_index = os.path.join(self.report_dir, "index.html")
            if os.path.exists(report_index):
                logger.info(f"报告文件已生成: {report_index}")
            else:
                logger.error(f"报告文件未生成! 目录内容: {os.listdir(self.report_dir)}")
        except subprocess.CalledProcessError as e:
            logger.error(f"生成报告失败: {e}")
        except Exception as e:
            logger.exception(f"生成报告时发生未知错误: {e}")

        return self.report_dir

    def get_report_path(self):
        """获取报告入口文件路径"""
        return os.path.join(self.report_dir, "index.html")
