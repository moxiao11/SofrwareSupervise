"""
Anomaly Detector
后台异常检测脚本
定期检测系统指标异常并生成告警
"""
import sys
import os
import time
import signal

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.services.monitoring_service import MonitoringService
from app.services.alert_service import AlertService
from app.core.logging import get_logger

# 检测间隔（秒）
DETECTION_INTERVAL = 10

# 运行标志
running = True


def signal_handler(signum, frame):
    """信号处理函数"""
    global running
    print("\n收到停止信号，正在退出...")
    running = False


def detect_anomalies():
    """检测异常"""
    logger = get_logger(service="anomaly-detector")

    # 注册信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("=" * 60)
    print("SmartOps 异常检测服务")
    print("=" * 60)
    print(f"检测间隔：{DETECTION_INTERVAL}秒")
    print("按 Ctrl+C 停止")
    print("=" * 60)

    while running:
        try:
            db = SessionLocal()
            monitoring_service = MonitoringService(db)
            alert_service = AlertService(db)

            # 采集系统指标（会自动触发异常检测）
            metrics = monitoring_service.collect_system_metrics(service="system")

            # 获取活跃告警数量
            active_alerts = alert_service.get_active_alerts(service="system")

            # 输出检测结果
            cpu_metric = next((m for m in metrics if m.metric_name == "cpu_usage"), None)
            memory_metric = next((m for m in metrics if m.metric_name == "memory_usage"), None)

            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            cpu_val = cpu_metric.metric_value if cpu_metric else 0
            mem_val = memory_metric.metric_value if memory_metric else 0

            print(f"[{timestamp}] CPU: {cpu_val}% | Memory: {mem_val}% | Active Alerts: {len(active_alerts)}")

            # 如果有活跃告警，显示最新告警
            if active_alerts:
                latest_alert = active_alerts[0]
                print(f"  ⚠️  [{latest_alert.severity}] {latest_alert.alert_type}: {latest_alert.message[:60]}...")

            db.close()

            # 等待下一次检测
            time.sleep(DETECTION_INTERVAL)

        except KeyboardInterrupt:
            print("\n异常检测服务已停止")
            break
        except Exception as e:
            logger.error(f"检测异常时出错：{e}")
            time.sleep(DETECTION_INTERVAL)


if __name__ == "__main__":
    detect_anomalies()
