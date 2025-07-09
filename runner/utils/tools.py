from urllib.parse import urlparse, urljoin


def is_absolute_url(url):
    """检查URL是否是绝对路径"""
    return bool(urlparse(url).netloc)


def normalize_url(base, path):
    """规范化URL处理"""
    if is_absolute_url(path):
        return path
    return urljoin(base, path)


def validate_url(url):
    """验证URL格式是否有效"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def get_domain(url):
    """获取URL的域名部分"""
    parsed = urlparse(url)
    return parsed.netloc


def get_path(url):
    """获取URL的路径部分"""
    parsed = urlparse(url)
    return parsed.path
