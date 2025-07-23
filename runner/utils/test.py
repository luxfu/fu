from functools import wraps


def decorator1(func):
    print("decorator1")

    @wraps(func)
    def wrapper(*args, **kwargs):
        print("in decorator1")
        return func(*args, **kwargs)
    return wrapper


def decorator2(func):
    print("decorator2")

    @wraps(func)
    def wrapper(*args, **kwargs):
        print("in decorator2")
        return func(*args, **kwargs)
    return wrapper


def decorator3(func):
    print("decorator3")

    @wraps(func)
    def wrapper(*args, **kwargs):
        print("in decorator3")
        return func(*args, **kwargs)
    return wrapper


@decorator1
@decorator2
@decorator3
def addNum(x, y):
    return x + y


def test(a=1, b=2, **params):
    print(**params)


if __name__ == '__main__':
    test(a=1, b=2, c=3)
