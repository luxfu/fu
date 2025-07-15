import allure
import pytest


@allure.epic("电商平台")
@allure.feature("购物车模块")
class TestShoppingCart:

    @allure.title("验证添加商品到购物车")
    @allure.story("用户操作流程")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.link("https://example.com/cart", name="需求文档")
    def test_add_to_cart(self):
        with allure.step("登录用户账号"):
            allure.dynamic.description("用户: test_user")
            assert True

        with allure.step("搜索商品并添加"):
            allure.attach("商品ID: 12345", name="商品信息",
                          attachment_type=allure.attachment_type.TEXT)
            assert 1 + 1 == 2

    @allure.title("删除购物车商品-失败用例")
    @allure.story("异常场景")
    def test_remove_from_cart_fail(self):
        with allure.step("初始化购物车"):
            cart_items = ["item1", "item2"]
            allure.attach(str(cart_items), name="初始购物车",
                          attachment_type=allure.attachment_type.JSON)

        with allure.step("删除不存在的商品"):
            assert "item3" not in cart_items  # 故意失败

    @pytest.mark.parametrize("item_id", [100, 200])
    def test_item_detail(self, item_id):
        allure.dynamic.title(f"检查商品详情页加载：ID={item_id}")
        with allure.step(f"访问商品ID {item_id}"):
            assert item_id in [100, 200]
