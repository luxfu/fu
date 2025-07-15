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
import time

logger = settings.LOGGER(__name__)


class SeleniumExecutor:
    def __init__(self, execution_id, driver=None):
        self.driver = driver or webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 10)
        self.report = AllureReportGenerator(execution_id)
        self.execution_id = execution_id
        self._create_environment_file()  # 创建环境文件

    def _create_environment_file(self):
        """创建环境信息文件"""
        env_info = {
            "测试套件": "未指定",
            "浏览器": self.driver.name,
            "浏览器版本": self.driver.capabilities.get('browserVersion', '未知'),
            "执行时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "平台": os.name,
            "Python版本": sys.version
        }

        # 在报告结果目录创建environment.properties文件
        env_file = os.path.join(self.report.results_dir,
                                "environment.properties")
        with open(env_file, "w", encoding="gbk") as f:
            for key, value in env_info.items():
                f.write(f"{key}={value}\n")

    def run_test_suite(self, test_suite: TestSuite):
        try:
            relations = test_suite.suitecaserelation_set.order_by('order')

            # 更新环境信息中的测试套件名称
            env_file = os.path.join(
                self.report.results_dir, "environment.properties")
            if os.path.exists(env_file):
                with open(env_file, "a", encoding="utf-8") as f:
                    f.write(f"测试套件={test_suite.name}\n")

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
            report_path = self.report.generate_report()
            logger.info(f"测试报告已生成: {report_path}")
            return report_path

    def execute_action(self, test_case: TestCase, test_suite: TestSuite):
        # 创建测试用例报告 - 使用新的参数格式
        tc_report = self.report.create_test_case(
            name=test_case.name,
            full_name=f"{test_suite.name}.{test_case.name}",
            suite=test_suite.name,
            tags=[f"case_id:{test_case.id}"]
        )

        try:
            logger.info(f"正在执行case id:{test_case.id}, po:{test_case.po}")

            # 导航到目标URL
            target_url = test_case.url
            if target_url:
                if not self.navigate_to_url(target_url):
                    self._handle_failure(
                        tc_report, Exception("导航失败"), "URL导航失败")
                    return False
            else:
                logger.warning("未指定URL，跳过导航步骤")

            # 定位元素
            locator_type, locator = (
                test_case.final_locator_type, test_case.final_locator)

            if not locator_type or not locator:
                self._handle_failure(tc_report, Exception("未指定定位器"), "元素定位失败")
                return False

            step = self.report.add_step(
                tc_report, f"定位元素: {locator}")
            logger.info(f"正在定位元素:{locator_type},{locator}")

            try:
                element = self.wait.until(
                    EC.presence_of_element_located((locator_type, locator))
                )
                self.report.add_screenshot(step, self.driver, "定位后截图")
            except Exception as e:
                self._handle_failure(tc_report, e, "元素定位失败")
                return False

            # 执行操作
            action_step = self.report.add_step(
                tc_report, f"执行操作: {test_case.action}")

            try:
                if test_case.action == 'click':
                    element.click()
                elif test_case.action == 'input':
                    element.clear()
                    element.send_keys(test_case.action_value)
                elif test_case.action == 'select':
                    from selenium.webdriver.support.select import Select
                    Select(element).select_by_visible_text(
                        test_case.action_value)
                # 添加其他操作处理...

                self.report.add_screenshot(action_step, self.driver, "操作后截图")
            except Exception as e:
                self._handle_failure(tc_report, e, "操作执行失败")
                return False

            # 执行断言
            if test_case.assert_type:
                assert_step = self.report.add_step(
                    tc_report, f"执行断言: {test_case.assert_type}")

                try:
                    if test_case.assert_type == 'text':
                        actual_text = element.text
                        if actual_text != test_case.assert_expression:
                            raise AssertionError(
                                f"文本断言失败: 期望 '{test_case.assert_expression}', 实际 '{actual_text}'"
                            )

                    elif test_case.assert_type == 'attr':
                        attr, expected_value = test_case.assert_expression.split(
                            '=', 1)
                        actual_value = element.get_attribute(attr)
                        if actual_value != expected_value:
                            raise AssertionError(
                                f"属性断言失败: 属性 '{attr}' 期望 '{expected_value}', 实际 '{actual_value}'"
                            )

                    # 添加其他断言处理...

                    # 断言成功
                    self.report.add_attachment(
                        assert_step,
                        "断言结果",
                        f"期望: {test_case.assert_expression}\n实际: 验证通过",
                        AttachmentType.TEXT
                    )

                except Exception as e:
                    # 断言失败处理
                    self._handle_failure(tc_report, e, "断言失败")
                    return False

        except Exception as e:
            # 其他异常
            self._handle_failure(tc_report, e, "未知错误")
            return False
        finally:
            # 确保最终完成测试用例
            self.report.finalize_test_case(tc_report)
            time.sleep(1)  # 短暂等待，确保操作完成

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

        # 添加错误详情附件
        self.report.add_attachment(
            error_step,
            "错误详情",
            f"错误类型: {type(exception).__name__}\n错误信息: {str(exception)}",
            AttachmentType.TEXT
        )

        # 添加失败截图
        try:
            self.report.add_screenshot(error_step, self.driver, "失败截图")
        except Exception as e:
            logger.error(f"截图失败: {e}")

        # 记录错误日志
        logger.error(f"{step_name}: {str(exception)}")
