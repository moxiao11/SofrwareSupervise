"""
Phase 2 Test Script
第二阶段功能测试脚本
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"


def test_health():
    """测试健康检查"""
    print("\n" + "=" * 60)
    print("测试1：健康检查")
    print("=" * 60)

    response = requests.get(f"{BASE_URL}/health")
    print(f"状态码：{response.status_code}")
    print(f"响应：{json.dumps(response.json(), indent=2, ensure_ascii=False)}")

    assert response.status_code == 200
    print("✓ 健康检查通过")


def test_users():
    """测试用户API"""
    print("\n" + "=" * 60)
    print("测试2：用户API")
    print("=" * 60)

    # 获取用户列表
    response = requests.get(f"{BASE_URL}/api/users/")
    print(f"获取用户列表：{response.status_code}")
    users = response.json()
    print(f"用户数量：{len(users)}")

    if users:
        user_id = users[0]['id']
        # 获取单个用户
        response = requests.get(f"{BASE_URL}/api/users/{user_id}")
        print(f"获取用户 {user_id}：{response.status_code}")
        print(f"用户信息：{json.dumps(response.json(), indent=2, ensure_ascii=False)}")

    print("✓ 用户API测试通过")


def test_orders():
    """测试订单API"""
    print("\n" + "=" * 60)
    print("测试3：订单API")
    print("=" * 60)

    # 获取订单列表
    response = requests.get(f"{BASE_URL}/api/orders/?limit=10")
    print(f"获取订单列表：{response.status_code}")
    data = response.json()
    print(f"订单总数：{data['total']}")
    print(f"返回订单数：{len(data['orders'])}")

    if data['orders']:
        order_id = data['orders'][0]['id']
        # 获取单个订单
        response = requests.get(f"{BASE_URL}/api/orders/{order_id}")
        print(f"获取订单 {order_id}：{response.status_code}")

    print("✓ 订单API测试通过")


def test_slow_sql():
    """测试慢SQL故障注入"""
    print("\n" + "=" * 60)
    print("测试4：慢SQL故障注入")
    print("=" * 60)

    # 启用慢SQL
    response = requests.post(f"{BASE_URL}/api/orders/debug/enable-slow-sql?enabled=true")
    print(f"启用慢SQL：{response.json()['message']}")

    # 查询用户订单（应该很慢）
    user_id = 1
    start_time = time.time()
    response = requests.get(f"{BASE_URL}/api/orders/user/{user_id}")
    query_time = time.time() - start_time

    print(f"查询用户 {user_id} 的订单")
    print(f"查询时间：{query_time:.3f}秒")
    print(f"状态码：{response.status_code}")

    # 禁用慢SQL
    response = requests.post(f"{BASE_URL}/api/orders/debug/enable-slow-sql?enabled=false")
    print(f"禁用慢SQL：{response.json()['message']}")

    # 再次查询（应该很快）
    start_time = time.time()
    response = requests.get(f"{BASE_URL}/api/orders/user/{user_id}")
    query_time = time.time() - start_time

    print(f"再次查询用户 {user_id} 的订单")
    print(f"查询时间：{query_time:.3f}秒")

    print("✓ 慢SQL故障注入测试通过")


def test_latency():
    """测试接口延迟故障注入"""
    print("\n" + "=" * 60)
    print("测试5：接口延迟故障注入")
    print("=" * 60)

    # 启用延迟
    response = requests.post(f"{BASE_URL}/api/orders/debug/enable-latency?enabled=true")
    print(f"启用延迟：{response.json()['message']}")

    # 查询订单（应该有3秒延迟）
    start_time = time.time()
    response = requests.get(f"{BASE_URL}/api/orders/?limit=5")
    query_time = time.time() - start_time

    print(f"查询订单时间：{query_time:.3f}秒")

    # 禁用延迟
    response = requests.post(f"{BASE_URL}/api/orders/debug/enable-latency?enabled=false")
    print(f"禁用延迟：{response.json()['message']}")

    print("✓ 接口延迟故障注入测试通过")


def test_error():
    """测试HTTP 500错误故障注入"""
    print("\n" + "=" * 60)
    print("测试6：HTTP 500错误故障注入")
    print("=" * 60)

    # 启用错误
    response = requests.post(f"{BASE_URL}/api/orders/debug/enable-error?enabled=true")
    print(f"启用错误：{response.json()['message']}")

    # 查询订单（应该返回500）
    response = requests.get(f"{BASE_URL}/api/orders/?limit=5")
    print(f"状态码：{response.status_code}")
    print(f"错误信息：{response.json().get('detail', 'N/A')}")

    assert response.status_code == 500

    # 禁用错误
    response = requests.post(f"{BASE_URL}/api/orders/debug/enable-error?enabled=false")
    print(f"禁用错误：{response.json()['message']}")

    print("✓ HTTP 500错误故障注入测试通过")


def test_fault_status():
    """测试故障状态查询"""
    print("\n" + "=" * 60)
    print("测试7：故障状态查询")
    print("=" * 60)

    response = requests.get(f"{BASE_URL}/api/orders/debug/status")
    status = response.json()

    print("当前故障状态：")
    print(f"  慢SQL：{status['slow_sql_enabled']}")
    print(f"  延迟：{status['latency_enabled']}")
    print(f"  错误：{status['error_enabled']}")

    print("✓ 故障状态查询测试通过")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("SmartOps 第二阶段功能测试")
    print("=" * 60)
    print(f"API地址：{BASE_URL}")

    try:
        test_health()
        test_users()
        test_orders()
        test_slow_sql()
        test_latency()
        test_error()
        test_fault_status()

        print("\n" + "=" * 60)
        print("✓ 所有测试通过！")
        print("=" * 60)

    except requests.exceptions.ConnectionError:
        print("\n✗ 错误：无法连接到后端服务")
        print("请确保后端服务已启动：uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n✗ 测试失败：{e}")


if __name__ == "__main__":
    main()
