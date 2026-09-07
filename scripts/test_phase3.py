"""
Phase 3 Test Script
第三阶段日志系统功能测试
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"


def test_log_api():
    """测试日志API"""
    print("\n" + "=" * 60)
    print("测试1：日志API")
    print("=" * 60)

    # 获取日志列表
    response = requests.get(f"{BASE_URL}/api/logs/?limit=10")
    print(f"获取日志列表：{response.status_code}")
    data = response.json()
    print(f"日志总数：{data['total']}")
    print(f"返回日志数：{len(data['logs'])}")

    if data['logs']:
        log = data['logs'][0]
        print(f"第一条日志：")
        print(f"  时间：{log['timestamp']}")
        print(f"  服务：{log['service']}")
        print(f"  级别：{log['level']}")
        print(f"  消息：{log['message']}")

    print("✓ 日志API测试通过")


def test_log_stats():
    """测试日志统计"""
    print("\n" + "=" * 60)
    print("测试2：日志统计")
    print("=" * 60)

    response = requests.get(f"{BASE_URL}/api/logs/stats/summary")
    print(f"日志统计：{response.status_code}")
    stats = response.json()
    print(f"  总数：{stats['total']}")
    print(f"  ERROR：{stats['error']}")
    print(f"  WARN：{stats['warn']}")
    print(f"  INFO：{stats['info']}")

    print("✓ 日志统计测试通过")


def test_service_list():
    """测试服务列表"""
    print("\n" + "=" * 60)
    print("测试3：服务列表")
    print("=" * 60)

    response = requests.get(f"{BASE_URL}/api/logs/services/list")
    print(f"服务列表：{response.status_code}")
    services = response.json()
    print(f"服务数量：{len(services)}")
    for service in services:
        print(f"  - {service}")

    print("✓ 服务列表测试通过")


def test_slow_sql_logging():
    """测试慢SQL日志记录"""
    print("\n" + "=" * 60)
    print("测试4：慢SQL日志记录")
    print("=" * 60)

    # 先查看当前日志数量
    response = requests.get(f"{BASE_URL}/api/logs/stats/summary")
    before_total = response.json()['total']
    print(f"测试前日志总数：{before_total}")

    # 启用慢SQL
    response = requests.post(f"{BASE_URL}/api/orders/debug/enable-slow-sql?enabled=true")
    print(f"启用慢SQL：{response.json()['message']}")

    # 查询用户订单（应该产生慢SQL日志）
    user_id = 1
    response = requests.get(f"{BASE_URL}/api/orders/user/{user_id}")
    print(f"查询用户 {user_id} 订单：{response.status_code}")

    # 禁用慢SQL
    response = requests.post(f"{BASE_URL}/api/orders/debug/enable-slow-sql?enabled=false")
    print(f"禁用慢SQL：{response.json()['message']}")

    # 等待日志写入
    time.sleep(1)

    # 再次查看日志数量
    response = requests.get(f"{BASE_URL}/api/logs/stats/summary")
    after_total = response.json()['total']
    print(f"测试后日志总数：{after_total}")
    print(f"新增日志：{after_total - before_total}")

    # 查询WARN级别日志
    response = requests.get(f"{BASE_URL}/api/logs/?level=WARN&limit=5")
    warn_logs = response.json()
    print(f"WARN日志数量：{warn_logs['total']}")

    if warn_logs['logs']:
        print("最新的WARN日志：")
        for log in warn_logs['logs'][:3]:
            print(f"  [{log['timestamp']}] {log['service']}: {log['message'][:80]}")

    print("✓ 慢SQL日志记录测试通过")


def test_log_filter():
    """测试日志过滤"""
    print("\n" + "=" * 60)
    print("测试5：日志过滤")
    print("=" * 60)

    # 按服务过滤
    response = requests.get(f"{BASE_URL}/api/logs/?service=order-service&limit=5")
    print(f"按服务过滤（order-service）：{response.status_code}")
    data = response.json()
    print(f"  日志数量：{data['total']}")

    # 按级别过滤
    response = requests.get(f"{BASE_URL}/api/logs/?level=INFO&limit=5")
    print(f"按级别过滤（INFO）：{response.status_code}")
    data = response.json()
    print(f"  日志数量：{data['total']}")

    # 关键词搜索
    response = requests.get(f"{BASE_URL}/api/logs/?keyword=Slow&limit=5")
    print(f"关键词搜索（Slow）：{response.status_code}")
    data = response.json()
    print(f"  日志数量：{data['total']}")

    print("✓ 日志过滤测试通过")


def test_create_log():
    """测试创建日志"""
    print("\n" + "=" * 60)
    print("测试6：创建日志")
    print("=" * 60)

    # 创建测试日志
    log_data = {
        "timestamp": "2026-09-07T10:00:00",
        "service": "test-service",
        "level": "INFO",
        "message": "这是一条测试日志",
        "trace_id": "test-trace-123",
        "metadata": {"test": True}
    }

    response = requests.post(f"{BASE_URL}/api/logs/", json=log_data)
    print(f"创建日志：{response.status_code}")

    if response.status_code == 201:
        log = response.json()
        print(f"  ID：{log['id']}")
        print(f"  服务：{log['service']}")
        print(f"  消息：{log['message']}")

    print("✓ 创建日志测试通过")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("SmartOps 第三阶段日志系统测试")
    print("=" * 60)
    print(f"API地址：{BASE_URL}")

    try:
        test_log_api()
        test_log_stats()
        test_service_list()
        test_slow_sql_logging()
        test_log_filter()
        test_create_log()

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
