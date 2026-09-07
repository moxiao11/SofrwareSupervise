"""
Metric Collector
后台指标采集脚本
定期采集系统指标（CPU、内存等）
"""
import sys
import os
import time
import signal

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.services.monitoring_service import MonitoringService
from app.core.logging import get_logger

# 采集间隔（秒）
COLLECTION_INTERVAL = 5

# 运行标志
running = True


def signal_handler(signum, frame):
    """信号处理函数"""
    global running
    print("\n收到停止信号，正在退出...")
    running = False


def collect_metrics():
    """采集指标"""
    logger = get_logger(service="metric-collector")

    # 注册信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("=" * 60)
    print("SmartOps 指标采集服务")
    print("=" * 60)
    print(f"采集间隔：{COLLECTION_INTERVAL}秒")
    print("按 Ctrl+C 停止")
    print("=" * 60)

    while running:
        try:
            db = SessionLocal()
            monitoring_service = MonitoringService(db)

            # 采集系统指标
            metrics = monitoring_service.collect_system_metrics(service="system")

            # 输出采集结果
            cpu_metric = next((m for m in metrics if m.metric_name == "cpu_usage"), None)
            memory_metric = next((m for m in metrics if m.metric_name == "memory_usage"), None)

            if cpu_metric and memory_metric:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] "
                      f"CPU: {cpu_metric.metric_value}% | "
                      f"Memory: {memory_metric.metric_value}%")

            db.close()

            # 等待下一次采集
            time.sleep(COLLECTION_INTERVAL)

        except KeyboardInterrupt:
            print("\n采集服务已停止")
            break
        except Exception as e:
            logger.error(f"采集指标时出错：{e}")
            time.sleep(COLLECTION_INTERVAL)


if __name__ == "__main__":
    collect_metrics()
