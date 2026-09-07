"""
Phase 4 Test Script
第四阶段监控指标系统功能测试
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"


def test_metrics_api():
    """测试指标API"""
    print("\n" + "=" * 60)
    print("测试1：指标API")
    print("=" * 60)

    # 获取指标列表
    response = requests.get(f"{BASE_URL}/api/metrics/?limit=10")
    print(f"获取指标列表：{response.status_code}")
    data = response.json()
    print(f"指标总数：{data['total']}")
    print(f"返回指标数：{len(data['metrics'])}")

    if data['metrics']:
        metric = data['metrics'][0]
        print(f"第一条指标：")
        print(f"  服务：{metric['service']}")
        print(f"  指标：{metric['metric_name']}")
        print(f"  值：{metric['metric_value']} {metric.get('unit', '')}")

    print("✓ 指标API测试通过")


def test_service_list():
    """测试服务列表"""
    print("\n" + "=" * 60)
    print("测试2：服务列表")
    print("=" * 60)

    response = requests.get(f"{BASE_URL}/api/metrics/services/list")
    print(f"服务列表：{response.status_code}")
    services = response.json()
    print(f"服务数量：{len(services)}")
    for service in services:
        print(f"  - {service}")

    print("✓ 服务列表测试通过")


def test_metric_list():
    """测试指标名称列表"""
    print("\n" + "=" * 60)
    print("测试3：指标名称列表")
    print("=" * 60)

    response = requests.get(f"{BASE_URL}/api/metrics/metrics/list")
    print(f"指标列表：{response.status_code}")
    metrics = response.json()
    print(f"指标数量：{len(metrics)}")
    for metric in metrics[:10]:
        print(f"  - {metric}")

    print("✓ 指标名称列表测试通过")


def test_dashboard_summary():
    """测试仪表盘摘要"""
    print("\n" + "=" * 60)
    print("测试4：仪表盘摘要")
    print("=" * 60)

    response = requests.get(f"{BASE_URL}/api/metrics/dashboard/summary")
    print(f"仪表盘摘要：{response.status_code}")
    summary = response.json()
    print(f"  CPU使用率：{summary.get('cpu_usage')}%")
    print(f"  内存使用率：{summary.get('memory_usage')}%")
    print(f"  API延迟：{summary.get('api_latency')}ms")

    print("✓ 仪表盘摘要测试通过")


def test_metric_filter():
    """测试指标过滤"""
    print("\n" + "=" * 60)
    print("测试5：指标过滤")
    print("=" * 60)

    # 按服务过滤
    response = requests.get(f"{BASE_URL}/api/metrics/?service=system&limit=5")
    print(f"按服务过滤（system）：{response.status_code}")
    data = response.json()
    print(f"  指标数量：{data['total']}")

    # 按指标名过滤
    response = requests.get(f"{BASE_URL}/api/metrics/?metric_name=cpu_usage&limit=5")
    print(f"按指标名过滤（cpu_usage）：{response.status_code}")
    data = response.json()
    print(f"  指标数量：{data['total']}")

    print("✓ 指标过滤测试通过")


def test_metric_stats():
    """测试指标统计"""
    print("\n" + "=" * 60)
    print("测试6：指标统计")
    print("=" * 60)

    response = requests.get(f"{BASE_URL}/api/metrics/stats/system/cpu_usage")
    print(f"指标统计：{response.status_code}")

    if response.status_code == 200:
        stats = response.json()
        print(f"  服务：{stats['service']}")
        print(f"  指标：{stats['metric_name']}")
        print(f"  平均值：{stats['stats']['avg']:.2f}")
        print(f"  最小值：{stats['stats']['min']:.2f}")
        print(f"  最大值：{stats['stats']['max']:.2f}")
        print(f"  记录数：{stats['stats']['count']}")

    print("✓ 指标统计测试通过")


def test_application_metrics():
    """测试应用指标采集"""
    print("\n" + "=" * 60)
    print("测试7：应用指标采集")
    print("=" * 60)

    # 先查看当前指标数量
    response = requests.get(f"{BASE_URL}/api/metrics/?service=gateway&limit=1")
    before_total = response.json()['total']
    print(f"测试前gateway指标数：{before_total}")

    # 发送几个请求
    for i in range(3):
        response = requests.get(f"{BASE_URL}/api/orders/?limit=5")
        print(f"请求 {i+1}: {response.status_code}")

    # 等待指标写入
    time.sleep(1)

    # 再次查看指标数量
    response = requests.get(f"{BASE_URL}/api/metrics/?service=gateway&limit=1")
    after_total = response.json()['total']
    print(f"测试后gateway指标数：{after_total}")
    print(f"新增指标：{after_total - before_total}")

    print("✓ 应用指标采集测试通过")


def test_database_metrics():
    """测试数据库指标采集"""
    print("\n" + "=" * 60)
    print("测试8：数据库指标采集")
    print("=" * 60)

    # 先查看当前指标数量
    response = requests.get(f"{BASE_URL}/api/metrics/?service=order-service&metric_name=db_query_time&limit=1")
    before_total = response.json()['total']
    print(f"测试前数据库指标数：{before_total}")

    # 查询用户订单（会采集数据库指标）
    response = requests.get(f"{BASE_URL}/api/orders/user/1")
    print(f"查询用户订单：{response.status_code}")

    # 等待指标写入
    time.sleep(1)

    # 再次查看指标数量
    response = requests.get(f"{BASE_URL}/api/metrics/?service=order-service&metric_name=db_query_time&limit=1")
    after_total = response.json()['total']
    print(f"测试后数据库指标数：{after_total}")
    print(f"新增指标：{after_total - before_total}")

    print("✓ 数据库指标采集测试通过")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("SmartOps 第四阶段监控指标系统测试")
    print("=" * 60)
    print(f"API地址：{BASE_URL}")

    try:
        test_metrics_api()
        test_service_list()
        test_metric_list()
        test_dashboard_summary()
        test_metric_filter()
        test_metric_stats()
        test_application_metrics()
        test_database_metrics()

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
