from runner.models import Tasks
from celery import shared_task
from core.executor import SeleniumExecutor
from django.conf import settings
from django.utils import timezone
import os
import logging
logger = logging.getLogger(__name__)


@shared_task
def run_test_suite(execution_id):
    execution = Tasks.objects.get(id=execution_id)
    execution.status = 'running'
    execution.save()

    try:
        executor = SeleniumExecutor(execution_id)
        report_path = executor.run_test_suite(execution.test_suite)

        if report_path:
            # 更新执行记录
            execution.status = 'passed' if executor.report.report_data[
                'status'] == 'passed' else 'failed'
            execution.report_path = report_path

            # 保存报告路径到数据库
            relative_path = os.path.relpath(report_path, settings.REPORTS_ROOT)
            execution.report_url = os.path.join(
                settings.MEDIA_URL, relative_path)
        else:
            execution.status = 'error'
    except Exception as e:
        logger.exception("测试执行发生错误")
        execution.status = 'error'
    finally:
        execution.end_time = timezone.now()
        execution.save()
