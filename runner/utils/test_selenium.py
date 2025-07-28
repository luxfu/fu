from selenium import webdriver
import time


def test():
    wd = webdriver.Chrome()
    wd.get("http://www.baidu.com")
    time.sleep(1)
    wd.get("https://blog.51cto.com/u_16213398/12168210")
    time.sleep(1)


if __name__ == "__main__":
    test()
