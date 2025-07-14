import os
import json
import shutil
import subprocess
import attr
from datetime import datetime
from allure_commons.types import AttachmentType
from allure_commons.model2 import TestResult, Status
from allure_commons.utils import uuid4, now


class AllureDemoGenerator:
    def __init__(self):
        # 创建报告目录结构
        self.report_dir = os.path.join(os.getcwd(), "allure-report")
        self.results_dir = os.path.join(self.report_dir, "results")
        os.makedirs(self.results_dir, exist_ok=True)

        # 存储测试用例数据
        self.test_cases = []

    def create_test_case(self, name, suite="Default Suite", tags=None):
        """创建测试用例"""
        test_case = {
            "uuid": str(uuid4()),
            "name": name,
            "fullName": f"{suite}.{name}",
            "labels": [
                {"name": "suite", "value": suite},
                {"name": "framework", "value": "allure-demo"}
            ],
            "links": [],
            "parameters": [],
            "steps": [],
            "attachments": [],
            "status": Status.PASSED,
            "statusDetails": None,
            "description": f"This is a test case for {name}",
            "start": now(),
            "stop": None,
            "historyId": str(uuid4()),
            "testCaseId": str(uuid4()),
            "stage": "scheduled"
        }

        if tags:
            for tag in tags:
                test_case["labels"].append({"name": "tag", "value": tag})

        self.test_cases.append(test_case)
        return test_case

    def add_step(self, test_case, name, status=Status.PASSED):
        """添加测试步骤"""
        step = {
            "name": name,
            "status": status,
            "start": now(),
            "stop": now(),
            "attachments": [],
            "parameters": [],
            "steps": []
        }

        test_case["steps"].append(step)

        # 更新测试用例状态
        if status != Status.PASSED and test_case["status"] == Status.PASSED:
            test_case["status"] = status

        return step

    def add_attachment(self, step, name, content_type="text/plain", content="Attachment content"):
        """添加附件"""
        attachment_uuid = str(uuid4())
        extension = {
            "text/plain": ".txt",
            "image/png": ".png",
            "application/json": ".json"
        }.get(content_type, ".bin")

        attachment_filename = f"{attachment_uuid}-attachment{extension}"
        attachment_path = os.path.join(self.results_dir, attachment_filename)

        # 保存附件内容
        if isinstance(content, str):
            with open(attachment_path, "w", encoding="utf-8") as f:
                f.write(content)
        elif isinstance(content, bytes):
            with open(attachment_path, "wb") as f:
                f.write(content)

        # 创建附件对象
        attachment = {
            "name": name,
            "source": attachment_filename,
            "type": content_type
        }

        step["attachments"].append(attachment)
        return attachment

    def finalize_test_case(self, test_case):
        """结束测试用例并保存结果"""
        test_case["stop"] = now()
        test_case["stage"] = "finished"

        # 创建 TestResult 对象
        test_result = TestResult(**test_case)

        # 序列化为字典
        result_dict = attr.asdict(test_result)

        # 保存为 JSON 文件
        result_file = os.path.join(
            self.results_dir, f"{test_case['uuid']}-result.json")
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(result_dict, f, indent=2)

        print(f"Saved test case: {result_file}")
        return result_file

    def generate_report(self):
        """生成 Allure 报告"""
        # 确保所有测试用例都已结束
        for test_case in self.test_cases:
            if not test_case.get("stop"):
                self.finalize_test_case(test_case)

        # 检查结果文件
        result_files = os.listdir(self.results_dir)
        if not result_files:
            print("No test result files found!")
            return

        # 生成报告命令
        report_cmd = [
            "allure", "generate",
            self.results_dir,
            "-o", self.report_dir,
            "--clean"
        ]

        print("Generating Allure report...")
        try:
            # 使用 shell=True 确保在 Windows 上也能正确找到 allure 命令
            subprocess.run(report_cmd, shell=True, check=True)
            report_index = os.path.join(self.report_dir, "index.html")
            print(f"Allure report generated successfully at: {report_index}")

            # 尝试在浏览器中打开报告
            if os.name == 'nt':  # Windows
                os.startfile(report_index)
            elif os.name == 'posix':  # macOS, Linux
                subprocess.run(["open", report_index])
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Failed to generate report: {e}")
            print("Make sure allure command is installed and in your PATH")
            print("You can manually generate the report with:")
            print(
                f"allure generate {self.results_dir} -o {self.report_dir} --clean")


def create_demo_data(generator):
    """创建演示数据"""
    print("Creating demo test data...")

    # 创建成功的测试用例
    success_case = generator.create_test_case(
        "Successful Test",
        suite="Demo Suite",
        tags=["demo", "success"]
    )
    step1 = generator.add_step(success_case, "Step 1: Setup")
    generator.add_attachment(
        step1,
        "Configuration",
        content_type="text/plain",
        content="Test configuration details"
    )

    step2 = generator.add_step(success_case, "Step 2: Execute action")
    generator.add_attachment(
        step2,
        "Request Data",
        content_type="application/json",
        content=json.dumps({"param1": "value1", "param2": 123}, indent=2)
    )

    # 创建失败的测试用例
    fail_case = generator.create_test_case(
        "Failed Test",
        suite="Demo Suite",
        tags=["demo", "failure"]
    )
    step_f1 = generator.add_step(fail_case, "Step 1: Setup", Status.PASSED)

    step_f2 = generator.add_step(
        fail_case, "Step 2: Execute action", Status.FAILED)
    generator.add_attachment(
        step_f2,
        "Error Details",
        content_type="text/plain",
        content="AssertionError: Expected 10 but got 8"
    )

    # 创建带截图的测试用例
    screenshot_case = generator.create_test_case(
        "Test with Screenshot",
        suite="Visual Tests",
        tags=["demo", "screenshot"]
    )
    step_s1 = generator.add_step(screenshot_case, "Take screenshot")

    # 创建简单的 PNG 图片作为演示
    # 实际使用中，这里应该使用 selenium 或其他工具的截图功能
    png_header = bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A])
    fake_png = png_header + b"..."  # 简化的 PNG 数据

    generator.add_attachment(
        step_s1,
        "Screenshot",
        content_type="image/png",
        content=fake_png
    )

    # 结束所有测试用例
    generator.finalize_test_case(success_case)
    generator.finalize_test_case(fail_case)
    generator.finalize_test_case(screenshot_case)


def main():
    # 初始化报告生成器
    generator = AllureDemoGenerator()

    # 创建演示数据
    create_demo_data(generator)

    # 生成报告
    generator.generate_report()

    print("Demo completed!")


if __name__ == "__main__":
    main()
