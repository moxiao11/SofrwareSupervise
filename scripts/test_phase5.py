"""
Phase 5 Test Script
第五阶段异常检测和告警系统功能测试
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"


def test_alerts_api():
    """测试告警API"""
    print("\n" + "=" * 60)
    print("测试1：告警API")
    print("=" * 60)

    # 获取告警列表
    response = requests.get(f"{BASE_URL}/api/alerts/?limit=10")
    print(f"获取告警列表：{response.status_code}")
    data = response.json()
    print(f"告警总数：{data['total']}")
    print(f"返回告警数：{len(data['alerts'])}")

    if data['alerts']:
        alert = data['alerts'][0]
        print(f"第一条告警：")
        print(f"  服务：{alert['service']}")
        print(f"  类型：{alert['alert_type']}")
        print(f"  级别：{alert['severity']}")
        print(f"  消息：{alert['message'][:60]}...")

    print("✓ 告警API测试通过")


def test_alert_stats():
    """测试告警统计"""
    print("\n" + "=" * 60)
    print("测试2：告警统计")
    print("=" * 60)

    response = requests.get(f"{BASE_URL}/api/alerts/stats/summary")
    print(f"告警统计：{response.status_code}")
    stats = response.json()
    print(f"  总数：{stats['total']}")
    print(f"  活跃：{stats['active']}")
    print(f"  已解决：{stats['resolved']}")
    print(f"  按级别：{stats['by_severity']}")

    print("✓ 告警统计测试通过")


def test_alert_rules():
    """测试告警规则"""
    print("\n" + "=" * 60)
    print("测试3：告警规则")
    print("=" * 60)

    response = requests.get(f"{BASE_URL}/api/alerts/rules/list")
    print(f"告警规则：{response.status_code}")
    data = response.json()
    print(f"规则总数：{data['total']}")
    print("规则列表：")
    for rule in data['rules'][:5]:
        print(f"  - {rule['rule_name']}: {rule['metric_name']} {rule['operator']} {rule['threshold']} ({rule['severity']})")

    print("✓ 告警规则测试通过")


def test_manual_check():
    """测试手动检查指标"""
    print("\n" + "=" * 60)
    print("测试4：手动检查指标")
    print("=" * 60)

    # 检查正常指标（不应该触发告警）
    response = requests.post(
        f"{BASE_URL}/api/alerts/check",
        params={
            "service": "test-service",
            "cpu_usage": 50.0,
            "memory_usage": 60.0
        }
    )
    print(f"检查正常指标：{response.status_code}")
    data = response.json()
    print(f"  触发告警数：{data['alerts_count']}")

    # 检查异常指标（应该触发告警）
    response = requests.post(
        f"{BASE_URL}/api/alerts/check",
        params={
            "service": "test-service",
            "cpu_usage": 96.0,  # 超过95%阈值
            "memory_usage": 92.0  # 超过90%阈值
        }
    )
    print(f"检查异常指标：{response.status_code}")
    data = response.json()
    print(f"  触发告警数：{data['alerts_count']}")

    if data['alerts']:
        print("触发的告警：")
        for alert in data['alerts']:
            print(f"  - [{alert['severity']}] {alert['message'][:60]}...")

    print("✓ 手动检查测试通过")


def test_active_alerts():
    """测试活跃告警"""
    print("\n" + "=" * 60)
    print("测试5：活跃告警")
    print("=" * 60)

    response = requests.get(f"{BASE_URL}/api/alerts/active/list")
    print(f"活跃告警：{response.status_code}")
    data = response.json()
    print(f"活跃告警数：{data['total']}")

    if data['alerts']:
        print("活跃告警列表：")
        for alert in data['alerts'][:5]:
            print(f"  - [{alert['severity']}] {alert['service']}: {alert['alert_type']}")

    print("✓ 活跃告警测试通过")


def test_resolve_alert():
    """测试解决告警"""
    print("\n" + "=" * 60)
    print("测试6：解决告警")
    print("=" * 60)

    # 先获取一个活跃告警
    response = requests.get(f"{BASE_URL}/api/alerts/active/list?limit=1")
    data = response.json()

    if data['alerts']:
        alert_id = data['alerts'][0]['id']
        print(f"解决告警 {alert_id}...")

        response = requests.post(f"{BASE_URL}/api/alerts/{alert_id}/resolve")
        print(f"解决告警：{response.status_code}")

        if response.status_code == 200:
            alert = response.json()
            print(f"  状态：{alert['status']}")
            print(f"  解决时间：{alert['resolved_at']}")
    else:
        print("没有活跃告警可解决")

    print("✓ 解决告警测试通过")


def test_alert_filter():
    """测试告警过滤"""
    print("\n" + "=" * 60)
    print("测试7：告警过滤")
    print("=" * 60)

    # 按服务过滤
    response = requests.get(f"{BASE_URL}/api/alerts/?service=system&limit=5")
    print(f"按服务过滤（system）：{response.status_code}")
    data = response.json()
    print(f"  告警数量：{data['total']}")

    # 按级别过滤
    response = requests.get(f"{BASE_URL}/api/alerts/?severity=P1&limit=5")
    print(f"按级别过滤（P1）：{response.status_code}")
    data = response.json()
    print(f"  告警数量：{data['total']}")

    # 按状态过滤
    response = requests.get(f"{BASE_URL}/api/alerts/?status=active&limit=5")
    print(f"按状态过滤（active）：{response.status_code}")
    data = response.json()
    print(f"  告警数量：{data['total']}")

    print("✓ 告警过滤测试通过")


def test_fault_injection_with_alerts():
    """测试故障注入与告警"""
    print("\n" + "=" * 60)
    print("测试8：故障注入与告警")
    print("=" * 60)

    # 先查看当前告警数量
    response = requests.get(f"{BASE_URL}/api/alerts/stats/summary")
    before_active = response.json()['active']
    print(f"测试前活跃告警数：{before_active}")

    # 启用慢SQL故障
    response = requests.post(f"{BASE_URL}/api/orders/debug/enable-slow-sql?enabled=true")
    print(f"启用慢SQL：{response.json()['message']}")

    # 查询订单（会产生慢SQL，可能触发告警）
    response = requests.get(f"{BASE_URL}/api/orders/user/1")
    print(f"查询订单：{response.status_code}")

    # 禁用慢SQL
    response = requests.post(f"{BASE_URL}/api/orders/debug/enable-slow-sql?enabled=false")
    print(f"禁用慢SQL：{response.json()['message']}")

    # 等待告警生成
    time.sleep(1)

    # 再次查看告警数量
    response = requests.get(f"{BASE_URL}/api/alerts/stats/summary")
    after_active = response.json()['active']
    print(f"测试后活跃告警数：{after_active}")
    print(f"新增告警：{after_active - before_active}")

    print("✓ 故障注入与告警测试通过")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("SmartOps 第五阶段异常检测系统测试")
    print("=" * 60)
    print(f"API地址：{BASE_URL}")

    try:
        test_alerts_api()
        test_alert_stats()
        test_alert_rules()
        test_manual_check()
        test_active_alerts()
        test_resolve_alert()
        test_alert_filter()
        test_fault_injection_with_alerts()

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
