import os
import sys
from .report import AllureReportGenerator
from allure_commons.types import AttachmentType
from allure_commons.model2 import Status
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from runner.models import TestCase, TestSuite
from django.conf import settings
from datetime import datetime
from django.conf import settings

logger = settings.LOGGER(__name__)


class SeleniumExecutor:
    def __init__(self, execution_id, driver=None):
        self.driver = driver or webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 10)
        self.report = AllureReportGenerator(execution_id)
        self.execution_id = execution_id

    def run_test_suite(self, test_suite: TestSuite):
        try:
            relations = test_suite.suitecaserelation_set.order_by('order')
            # 添加环境信息
            self._add_environment_info(test_suite)

            for relation in relations:
                test_case = relation.test_case
                if not self.execute_action(test_case, test_suite):
                    logger.error(f"用例 {test_case.name} 执行失败")
                    # 可选：是否继续执行后续用例
                    if not settings.CONTINUE_ON_FAILURE:
                        break
            return True
        except Exception as e:
            logger.exception(f"测试套件执行失败:{e}")
            return False
        finally:
            self.driver.quit()
            # 生成最终报告
            report_path = self.report.finalize_report()
            return report_path

    def execute_action(self, test_case: TestCase, test_suite: TestSuite):
        # 创建测试用例报告
        tc_report = self.report.create_test_case(
            name=test_case.name,
            suite=test_suite.name,
            tags=[f"case_id:{test_case.id}"]
        )

        try:
            logger.info(f"正在执行case id:{test_case.id},po:{test_case.po}")
            # 获取最终URL
            base_url = test_suite.get_environment_url()
            target_url = test_case.get_final_url(base_url)

            if target_url:
                self.navigate_to_url(target_url)
            if not target_url:
                logger.error("未指定URL，无法执行操作")
                return False

            # 未导航到目标URL
            if not self.navigate_to_url(target_url):
                return False
            # 定位元素
            locator_type, locator = (
                test_case.final_locator_type, test_case.final_locator)
            if not locator_type or not locator:
                return False
            step = self.report.add_step(
                tc_report, f"定位元素: {locator}")
            logger.info(f"正在定位元素:{locator_type},{locator}")
            element = self.wait.until(
                EC.presence_of_element_located(
                    (locator_type, locator)
                )
            )
            self.report.add_screenshot(step, self.driver, "定位后截图")

            # 执行操作
            action_step = self.report.add_step(
                tc_report, f"执行操作: {test_case.action}")
            if test_case.action == 'click':
                element.click()
            elif test_case.action == 'input':
                element.clear()
                element.send_keys(test_case.action_value)
            # ...其他操作处理

            self.report.add_screenshot(action_step, self.driver, "操作后截图")

            # 执行断言
            if test_case.assert_type:
                assert_step = self.report.add_step(
                    tc_report, f"执行断言: {test_case.assert_type}")
                if test_case.assert_type == 'text':
                    assert element.text == test_case.assert_expression
                elif test_case.assert_type == 'attr':
                    attr, value = test_case.assert_expression.split('=')
                    assert element.get_attribute(attr) == value
                # ...其他断言处理

                self.report.add_attachment(
                    assert_step,
                    "断言结果",
                    f"期望: {test_case.assert_expression}\n实际: 验证通过",
                    AttachmentType.TEXT
                )

            # 更新统计
            self.report.report_data["statistics"]["passed"] += 1

        except AssertionError as e:
            # 断言失败处理
            self._handle_failure(tc_report, e, "断言失败")
            return False
        except WebDriverException as e:
            # 元素操作失败
            self._handle_failure(tc_report, e, "操作失败")
            return False
        except Exception as e:
            # 其他异常
            self._handle_failure(tc_report, e, "未知错误")
            return False
        finally:
            self.report.finalize_test_case(tc_report)

        return True

    def navigate_to_url(self, url):
        """导航到指定URL，处理可能的异常"""
        try:
            current_url = self.driver.current_url
            if current_url == url:
                logger.info(f"已在目标页面: {url}")
                return True

            logger.info(f"导航到: {url}")
            self.driver.get(url)

            # 等待页面加载完成
            WebDriverWait(self.driver, 10).until(
                lambda d: d.execute_script(
                    'return document.readyState') == 'complete'
            )
            return True
        except WebDriverException as e:
            logger.error(f"导航失败: {str(e)}")
            return False

    def _handle_failure(self, tc_report, exception, step_name):
        error_step = self.report.add_step(tc_report, step_name, Status.FAILED)
        self.report.add_attachment(
            error_step,
            "错误详情",
            f"错误类型: {type(exception).__name__}\n错误信息: {str(exception)}",
            AttachmentType.TEXT
        )
        self.report.add_screenshot(error_step, self.driver, "失败截图")

        # 更新统计
        self.report.report_data["statistics"]["failed"] += 1

    def _add_environment_info(self, test_suite):
        # 添加环境信息到报告
        env_info = {
            "测试套件": test_suite.name,
            "浏览器": self.driver.name,
            "浏览器版本": self.driver.capabilities['browserVersion'],
            "执行时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "平台": os.name,
            "Python版本": sys.version
        }

        env_file = os.path.join(self.report.results_dir,
                                "environment.properties")
        with open(env_file, "w") as f:
            for key, value in env_info.items():
                f.write(f"{key}={value}\n")
