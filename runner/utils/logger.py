import logging
import os
from logging.handlers import RotatingFileHandler
from django.conf import settings


def setup_logger(
    logger_name,
    log_level=logging.DEBUG,
    console_level=logging.INFO,
    log_dir="logs",
    backup_count=7  # 保留7天的日志
):
    """
    配置并返回一个带有StreamHandler和FileHandler的logger

    参数:
        logger_name: logger的名称
        log_level: 文件日志的级别
        console_level: 控制台日志的级别
        log_dir: 日志文件存储目录
        backup_count: 保留的旧日志文件数量
    """

    # 创建logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)  # 设置最低级别，实际级别由handler控制

    # 避免重复添加handler
    if logger.hasHandlers():
        logger.handlers.clear()

    # 确保日志目录存在
    os.makedirs(log_dir, exist_ok=True)

    # 1. 创建并配置控制台处理器 (StreamHandler)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)

    # 2. 创建并配置文件处理器 (TimedRotatingFileHandler - 按天轮转)
    server_file_handler = RotatingFileHandler(
        filename=settings.SERVER_LOGS_FILE,
        maxBytes=1024 * 1024 * 100,
        backupCount=backup_count,
        encoding="utf-8"
    )
    server_file_handler.setLevel(log_level)

    # 3. 创建错误日志处理器 (单独记录ERROR及以上日志)
    error_handler = RotatingFileHandler(
        filename=settings.ERROR_LOGS_FILE,
        maxBytes=1024 * 1024 * 100,
        backupCount=backup_count,
        encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)

    # 创建格式化器
    console_format = logging.Formatter(
        "[%(asctime)s][%(name)s.%(funcName)s():%(lineno)d] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    file_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 应用格式化器
    console_handler.setFormatter(console_format)
    server_file_handler.setFormatter(file_format)
    error_handler.setFormatter(file_format)

    # 将处理器添加到logger
    logger.addHandler(console_handler)
    logger.addHandler(server_file_handler)
    logger.addHandler(error_handler)

    # 添加一个过滤器，避免SQL日志等过于冗长
    class InfoFilter(logging.Filter):
        def filter(self, record):
            # 忽略低于INFO级别的日志（DEBUG级别）
            return record.levelno >= logging.INFO

    # 应用过滤器到文件处理器（不过滤错误日志）
    server_file_handler.addFilter(InfoFilter())

    return logger


# 使用示例
if __name__ == "__main__":
    # 设置日志
    logger = setup_logger(
        "my_app",
        log_level=logging.DEBUG,  # 文件记录DEBUG及以上
        console_level=logging.INFO  # 控制台只显示INFO及以上
    )

    # 测试不同级别的日志
    logger.debug("这是一条DEBUG信息 - 通常只在文件中看到")
    logger.info("这是一条INFO信息")
    logger.warning("这是一条WARNING信息")
    logger.error("这是一条ERROR信息")
    logger.critical("这是一条CRITICAL信息")

    try:
        1 / 0
    except Exception as e:
        logger.exception("发生了一个异常: %s", e)
