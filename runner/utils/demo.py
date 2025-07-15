import os
import json
import subprocess
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from allure_commons.types import AttachmentType
from allure_commons.model2 import Status


class AllureReportGenerator:
    def __init__(self, execution_id: str):
        self.execution_id = execution_id
        self.report_dir = self._get_report_dir()
        self.results_dir = os.path.join(self.report_dir, "results")
        self.attachments_dir = os.path.join(self.results_dir, "attachments")

        # 创建目录
        os.makedirs(self.results_dir, exist_ok=True)
        os.makedirs(self.attachments_dir, exist_ok=True)

        # 存储测试用例和容器
        self.test_cases: Dict[str, dict] = {}  # uuid -> test_case
        self.containers: Dict[str, dict] = {}  # container_uuid -> container
        self.global_containers: List[str] = []  # 全局容器UUID列表

        # 记录开始时间
        self.start_time = int(datetime.utcnow().timestamp() * 1000)

    def _get_report_dir(self) -> str:
        base_dir = "reports1"  # 可根据需要修改
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(base_dir, f"execution_{self.execution_id}_{timestamp}")

    def create_container(self, name: str, children: List[str] = None,
                         befores: List[dict] = None, afters: List[dict] = None) -> str:
        """创建容器文件"""
        container_uuid = str(uuid.uuid4())
        container = {
            "uuid": container_uuid,
            "name": name,
            "children": children or [],
            "befores": befores or [],
            "afters": afters or [],
            "start": self.start_time,
            "stop": int(datetime.utcnow().timestamp() * 1000)
        }
        self.containers[container_uuid] = container
        self.global_containers.append(container_uuid)
        return container_uuid

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
            "status": Status.PASSED,
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
                {"name": "framework", "value": "custom-framework"}
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
        return test_case

    def add_step(self, test_case: dict, name: str, status: Status = Status.PASSED) -> dict:
        """添加步骤到测试用例"""
        step = {
            "name": name,
            "status": status,
            "start": int(datetime.utcnow().timestamp() * 1000),
            "stop": int(datetime.utcnow().timestamp() * 1000),
            "attachments": []
        }
        test_case["steps"].append(step)

        # 更新测试用例状态：如果步骤失败且当前用例状态是通过，则更新状态
        if status != Status.PASSED and test_case["status"] == Status.PASSED:
            test_case["status"] = status

        return step

    def add_attachment(self, step: dict, name: str, content: str, attachment_type: AttachmentType) -> str:
        """添加附件到步骤"""
        attachment_uuid = str(uuid.uuid4())
        extension = attachment_type.extension
        filename = f"{attachment_uuid}-attachment{extension}"
        filepath = os.path.join(self.attachments_dir, filename)

        # 保存附件内容
        with open(filepath, "w") as f:
            f.write(content)

        # 记录附件信息
        attachment = {
            "name": name,
            "source": filename,
            "type": attachment_type.value[0]  # 取MIME类型，例如'image/png'
        }
        step["attachments"].append(attachment)
        return filepath

    def add_screenshot(self, step: dict, name: str = "Screenshot", content: Optional[bytes] = None) -> str:
        """添加截图附件"""
        if content is None:
            # 生成一个简单的PNG文件头作为示例
            content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDAT\x08\xd7c\xf8\x0f\x04\x00\x01\x01\x01\x00\x18\xdd\x8b\xd0\x00\x00\x00\x00IEND\xaeB`\x82'
        return self.add_attachment(step, name, content, AttachmentType.PNG)

    def finalize_test_case(self, test_case: dict):
        """结束测试用例：设置停止时间并保存为result.json文件"""
        test_case["stop"] = int(datetime.utcnow().timestamp() * 1000)

        # 保存为result.json文件
        result_file = os.path.join(
            self.results_dir, f"{test_case['uuid']}-result.json")
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(test_case, f, ensure_ascii=False, indent=2)

    def generate_container_files(self):
        """生成所有容器文件"""
        # 首先创建用例级别的容器
        for test_uuid in self.test_cases:
            container_uuid = str(uuid.uuid4())
            container = {
                "uuid": container_uuid,
                "children": [test_uuid],
                "befores": [{
                    "name": "_skip_sensitive",
                    "status": Status.PASSED,
                    "start": self.start_time,
                    "stop": self.start_time
                }],
                "start": self.start_time,
                "stop": int(datetime.utcnow().timestamp() * 1000)
            }
            self.containers[container_uuid] = container
            self.global_containers.append(container_uuid)

        # 然后创建全局容器
        global_container_uuid = str(uuid.uuid4())
        global_container = {
            "uuid": global_container_uuid,
            "children": list(self.test_cases.keys()),
            "befores": [{
                "name": "sensitive_url",
                "status": Status.PASSED,
                "start": self.start_time,
                "stop": self.start_time
            }],
            "start": self.start_time,
            "stop": int(datetime.utcnow().timestamp() * 1000)
        }
        self.containers[global_container_uuid] = global_container
        self.global_containers.append(global_container_uuid)

        # 保存所有容器文件
        for container_uuid, container_data in self.containers.items():
            container_file = os.path.join(
                self.results_dir, f"{container_uuid}-container.json")
            with open(container_file, "w", encoding="utf-8") as f:
                json.dump(container_data, f, ensure_ascii=False, indent=2)

    def generate_report(self):
        """生成完整的Allure报告"""
        # 1. 完成所有测试用例
        for test_case in self.test_cases.values():
            if not test_case.get("stop"):
                self.finalize_test_case(test_case)

        # 2. 生成容器文件
        self.generate_container_files()

        # 3. 生成Allure报告
        report_cmd = [
            "allure", "generate", self.results_dir,
            "-o", self.report_dir, "--clean"
        ]
        try:
            subprocess.run(report_cmd, check=True, shell=True)
            print(
                f"Allure report generated at: {os.path.join(self.report_dir, 'index.html')}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to generate Allure report: {e}")

        return self.report_dir


# 示例用法
if __name__ == "__main__":
    # 初始化报告生成器
    report_gen = AllureReportGenerator("demo_execution")

    # 创建全局容器
    report_gen.create_container("Global Container")

    # 创建测试用例1 - 验证添加商品到购物车
    test_case1 = report_gen.create_test_case(
        name="验证添加商品到购物车",
        full_name="shopping_cart.TestAddToCart#test_add_product",
        suite="shopping_cart",
        description="用户: test_user",
        tags=["smoke", "cart"],
        epic="电商平台",
        feature="购物车模块",
        story="用户操作流程",
        severity="critical",
        links=[{"type": "link", "url": "https://example.com/cart", "name": "需求文档"}]
    )

    # 添加步骤1
    step1 = report_gen.add_step(test_case1, "登录用户账号")

    # 添加步骤2
    step2 = report_gen.add_step(test_case1, "搜索商品并添加")
    # 添加附件（文本）
    report_gen.add_attachment(
        step2,
        "商品信息",
        "商品ID: 12345",
        AttachmentType.TEXT
    )

    # 创建测试用例2 - 删除购物车商品（失败用例）
    test_case2 = report_gen.create_test_case(
        name="删除购物车商品-失败用例",
        full_name="shopping_cart.TestRemoveFromCart#test_remove_product_fail",
        suite="shopping_cart",
        story="异常场景",
        epic="电商平台",
        feature="购物车模块"
    )

    # 添加步骤1
    step1 = report_gen.add_step(test_case2, "初始化购物车")
    # 添加附件（JSON）
    report_gen.add_attachment(
        step1,
        "初始购物车",
        '["item1", "item2"]',
        AttachmentType.JSON
    )

    # 添加步骤2（失败步骤）
    step2 = report_gen.add_step(test_case2, "删除不存在的商品", Status.FAILED)

    # 创建测试用例3 - 参数化测试
    for item_id in [100, 200]:
        test_case3 = report_gen.create_test_case(
            name=f"检查商品详情页加载：ID={item_id}",
            full_name="shopping_cart.TestItemDetail#test_item_detail",
            suite="shopping_cart",
            epic="电商平台",
            feature="购物车模块"
        )
        # 添加参数
        test_case3["parameters"] = [{"name": "item_id", "value": str(item_id)}]

        # 添加步骤
        step = report_gen.add_step(test_case3, f"访问商品ID {item_id}")

        # 完成测试用例
        report_gen.finalize_test_case(test_case3)

    # 完成测试用例
    report_gen.finalize_test_case(test_case1)
    report_gen.finalize_test_case(test_case2)

    # 生成报告
    report_dir = report_gen.generate_report()
    print(f"Report generated: {report_dir}")
