from playwright.async_api import Page, expect, async_playwright
from playwright.sync_api import sync_playwright, expect as expect_sync
import time
import asyncio


async def test(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="msedge", headless=False)
        page = await browser.new_page()
        page1 = await browser.new_page()
        await page.goto(url)
        await page1.goto(url)
        await browser.close()


def test1():
    with sync_playwright() as p:
        b = p.chromium.launch(headless=False, slow_mo=100)
        page = b.new_page()
        page.goto("http:www.baidu.com")
        page.locator('#kw').fill('测试')
        page.locator('#su').click()
        # expect_sync(page.locator('#su')).to_be_hidden()
        page.get_attribute
        b.close()


def test2():
    with sync_playwright() as p:
        b = p.chromium.launch(headless=False, slow_mo=5000)
        context = b.new_context(storage_state='./x.json')
        p = context.new_page()
        p.goto("https://chat.deepseek.com/")


if __name__ == "__main__":
    # asyncio.run(test("http:www.baidu.com"))
    test1()
    test2()
    # asyncio.run(test("https://playwright.net.cn/python/docs/library"))
