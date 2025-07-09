from typing import Any
from django.db import models
from urllib.parse import urljoin
# Create your models here.


class PageObject(models.Model):
    LOCATOR_TYPES = (
        ('id', 'ID'),
        ('xpath', 'XPath'),
        ('css', 'CSS'),
        ('name', 'Name'),
        ('class', 'Class Name'),
        ('link', 'Link Text'),
    )

    name = models.CharField("元素名称", max_length=100)
    locator = models.CharField("定位表达式", max_length=255)
    locator_type = models.CharField(
        "定位方式", max_length=10, choices=LOCATOR_TYPES)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    url = models.CharField("页面URL", max_length=255,
                           help_text="页面基础URL，可以是绝对或相对路径")
    is_relative = models.BooleanField("相对路径", default=True,
                                      help_text="如果是相对路径，执行时会与基础URL拼接")

    # 获取完整URL的方法
    def get_full_url(self, base_url):
        if self.is_relative:
            return urljoin(base_url, self.url)
        return self.url

    class Meta:
        db_table = "pageobject"
        verbose_name = "页面对象"
        unique_together = ('name', 'locator_type', 'locator')


class TestCase(models.Model):
    ACTION_TYPES = (
        ('click', '点击'),
        ('input', '输入'),
        ('select', '选择'),
        ('hover', '悬停'),
        ('scroll', '滚动'),
        ('switch', '窗口切换'),
    )
    ASSERT_TYPES = (
        ('text', '文本验证'),
        ('attr', '属性验证'),
        ('url', 'URL验证'),
        ('title', '标题验证'),
        ('exist', '元素存在'),
    )

    name = models.CharField("用例名称", max_length=100)
    url = models.CharField("页面URL", max_length=255, blank=True, null=True,
                           help_text="如果不使用PO的URL，可单独指定")
    url_override = models.BooleanField("覆盖PO的URL", default=False,
                                       help_text="勾选后使用此URL而非PO的URL")
    po = models.ForeignKey(
        PageObject, on_delete=models.SET_NULL, null=True, blank=True)
    custom_locator = models.CharField("自定义定位", max_length=255, blank=True)
    custom_locator_type = models.CharField(
        "定位方式", max_length=10, choices=PageObject.LOCATOR_TYPES, blank=True)
    action = models.CharField("操作类型", max_length=20, choices=ACTION_TYPES)
    action_value = models.CharField(
        "操作值", max_length=255, blank=True, null=True)  # 输入文本/选择值等
    assert_type = models.CharField(
        "断言类型", max_length=20, choices=ASSERT_TYPES, blank=True)
    assert_expression = models.CharField("断言表达式", max_length=255, blank=True)
    order = models.PositiveIntegerField("执行顺序", default=0)

    # 获取最终URL的方法
    def get_final_url(self, base_url):
        # 优先使用用例自身的URL（如果设置了覆盖）
        if self.url and self.url_override:
            return self.url

        # 其次使用关联PO的URL
        if self.po:
            return self.po.get_full_url(base_url)

        # 最后使用用例自身的URL（如果不覆盖）
        if self.url:
            return self.po.get_full_url(base_url)

        return None  # 如果没有URL，应由调用方处理

    @property
    def final_locator(self):
        return self.po.locator if self.po else self.custom_locator

    @property
    def final_locator_type(self):
        return self.po.locator_type if self.po else self.custom_locator_type


class TestSuite(models.Model):
    STATUS_CHOICES = (
        ('draft', '草稿'),
        ('active', '激活'),
        ('archived', '归档'),
    )
    # 环境变量配置
    ENVIRONMENT_CHOICES = (
        ('dev', '开发环境'),
        ('test', '测试环境'),
        ('staging', '预发布环境'),
        ('prod', '生产环境'),
    )
    name = models.CharField("用例集名称", max_length=100)
    # ... 其他字段 ...
    base_url = models.CharField("基础URL", max_length=255, default="http://localhost",
                                help_text="所有相对URL将基于此URL拼接")

    environment = models.CharField(
        "运行环境", max_length=20, choices=ENVIRONMENT_CHOICES, default='test')
    test_cases = models.ManyToManyField(TestCase, through='SuiteCaseRelation')
    status = models.CharField(
        "状态", max_length=10, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    # 获取环境特定的基础URL

    def get_environment_url(self):
        env_urls = {
            'dev': 'http://dev.example.com',
            'test': 'http://test.example.com',
            'staging': 'http://staging.example.com',
            'prod': 'http://prod.example.com',
        }
        return env_urls.get(self.environment, self.base_url)


class SuiteCaseRelation(models.Model):
    test_suite = models.ForeignKey(TestSuite, on_delete=models.CASCADE)
    test_case = models.ForeignKey(TestCase, on_delete=models.CASCADE)
    order = models.PositiveIntegerField("执行顺序")

    class Meta:
        ordering = ['order']


class TestExecution(models.Model):
    STATUS_CHOICES = (
        ('pending', '排队中'),
        ('running', '执行中'),
        ('passed', '通过'),
        ('failed', '失败'),
        ('error', '错误'),
    )

    test_suite = models.ForeignKey(TestSuite, on_delete=models.CASCADE)
    start_time = models.DateTimeField("开始时间", auto_now_add=True)
    end_time = models.DateTimeField("结束时间", null=True)
    status = models.CharField(
        "状态", max_length=10, choices=STATUS_CHOICES, default='pending')
    report_url = models.URLField("报告链接", blank=True)
    log_path = models.CharField("日志路径", max_length=255, blank=True)
    executor = models.CharField("执行人", max_length=50, blank=True)


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
