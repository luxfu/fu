from typing import Any
from django.db import models

# Create your models here.


class FormatDateTimeField(models.DateTimeField):
    def get_prep_value(self, value: Any) -> Any:
        value = super().get_prep_value(value)
        if value is not None and hasattr(value, 'microsecond'):
            value = value.replace(microsecond=0)
        return value


class Project(models.Model):
    # id = models.AutoField(primary_key=True) 不需要显示声明，自动创建
    name = models.CharField(max_length=20, verbose_name="项目名称")
    chioces = [
        (0, "未开始"),
        (1, "进行中"),
        (2, "暂停中"),
        (3, "已完成"),
        (4, "已终止"),
    ]
    status = models.SmallIntegerField(
        choices=chioces, verbose_name="项目状态", default=0)
    create_time = FormatDateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.name, self.id, self.status, self.create_time}"

    class Meta:
        db_table = "project"
        verbose_name = "项目project"
        verbose_name_plural = "项目"
        ordering = ["-create_time"]  # 默认时间降序
