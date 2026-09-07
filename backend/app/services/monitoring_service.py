"""
Monitoring Service
监控服务 - 指标采集与管理
"""
import psutil
from datetime import datetime
from sqlalchemy.orm import Session
from typing import Optional, List
from decimal import Decimal

from app.models.monitor_metric import MonitorMetric
from app.schemas.monitor_metric import MetricCreate, MetricFilter
from app.core.logging import get_logger


class MonitoringService:
    """监控服务类"""

    def __init__(self, db: Session):
        self.db = db
        self.logger = get_logger(service="monitoring-service")

    def collect_system_metrics(self, service: str = "system"):
        """
        采集系统指标（CPU、内存、磁盘等）
        """
        metrics = []

        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            metrics.append(self.create_metric(
                service=service,
                metric_name="cpu_usage",
                metric_value=Decimal(str(cpu_percent)),
                unit="percent"
            ))

            # 内存使用
            memory = psutil.virtual_memory()
            metrics.append(self.create_metric(
                service=service,
                metric_name="memory_usage",
                metric_value=Decimal(str(memory.percent)),
                unit="percent"
            ))
            metrics.append(self.create_metric(
                service=service,
                metric_name="memory_used",
                metric_value=Decimal(str(memory.used / (1024**3))),  # GB
                unit="GB"
            ))
            metrics.append(self.create_metric(
                service=service,
                metric_name="memory_total",
                metric_value=Decimal(str(memory.total / (1024**3))),  # GB
                unit="GB"
            ))

            # 磁盘使用
            disk = psutil.disk_usage('/')
            metrics.append(self.create_metric(
                service=service,
                metric_name="disk_usage",
                metric_value=Decimal(str(disk.percent)),
                unit="percent"
            ))

            # 网络IO（如果有）
            try:
                net_io = psutil.net_io_counters()
                metrics.append(self.create_metric(
                    service=service,
                    metric_name="network_bytes_sent",
                    metric_value=Decimal(str(net_io.bytes_sent / (1024**2))),  # MB
                    unit="MB"
                ))
                metrics.append(self.create_metric(
                    service=service,
                    metric_name="network_bytes_recv",
                    metric_value=Decimal(str(net_io.bytes_recv / (1024**2))),  # MB
                    unit="MB"
                ))
            except Exception as e:
                self.logger.warning(f"Failed to collect network metrics: {e}")

            self.logger.info(f"Collected system metrics for {service}")

        except Exception as e:
            self.logger.error(f"Failed to collect system metrics: {e}")

        return metrics

    def collect_application_metrics(
        self,
        service: str,
        latency_ms: float,
        status_code: int,
        error: bool = False
    ):
        """
        采集应用指标（API延迟、错误率等）
        """
        metrics = []

        # API延迟
        metrics.append(self.create_metric(
            service=service,
            metric_name="api_latency",
            metric_value=Decimal(str(latency_ms)),
            unit="ms"
        ))

        # HTTP状态码
        metrics.append(self.create_metric(
            service=service,
            metric_name="http_status",
            metric_value=Decimal(str(status_code)),
            unit="code"
        ))

        # 错误标记
        if error:
            metrics.append(self.create_metric(
                service=service,
                metric_name="error_count",
                metric_value=Decimal("1"),
                unit="count"
            ))

        return metrics

    def collect_database_metrics(
        self,
        service: str,
        query_time_ms: float,
        connections: Optional[int] = None
    ):
        """
        采集数据库指标
        """
        metrics = []

        # 查询时间
        metrics.append(self.create_metric(
            service=service,
            metric_name="db_query_time",
            metric_value=Decimal(str(query_time_ms)),
            unit="ms"
        ))

        # 连接数（如果提供）
        if connections is not None:
            metrics.append(self.create_metric(
                service=service,
                metric_name="db_connections",
                metric_value=Decimal(str(connections)),
                unit="count"
            ))

        return metrics

    def create_metric(
        self,
        service: str,
        metric_name: str,
        metric_value: Decimal,
        unit: Optional[str] = None
    ) -> MonitorMetric:
        """
        创建指标记录
        """
        metric = MonitorMetric(
            service=service,
            metric_name=metric_name,
            metric_value=metric_value,
            unit=unit,
            timestamp=datetime.now()
        )
        self.db.add(metric)
        self.db.commit()
        self.db.refresh(metric)
        return metric

    def get_metrics(
        self,
        filter: Optional[MetricFilter] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[MonitorMetric]:
        """
        查询指标列表
        """
        query = self.db.query(MonitorMetric)

        if filter:
            if filter.service:
                query = query.filter(MonitorMetric.service == filter.service)
            if filter.metric_name:
                query = query.filter(MonitorMetric.metric_name == filter.metric_name)
            if filter.start_time:
                query = query.filter(MonitorMetric.timestamp >= filter.start_time)
            if filter.end_time:
                query = query.filter(MonitorMetric.timestamp <= filter.end_time)

        query = query.order_by(MonitorMetric.timestamp.desc())
        metrics = query.offset(skip).limit(limit).all()

        return metrics

    def count_metrics(self, filter: Optional[MetricFilter] = None) -> int:
        """
        统计指标数量
        """
        query = self.db.query(MonitorMetric)

        if filter:
            if filter.service:
                query = query.filter(MonitorMetric.service == filter.service)
            if filter.metric_name:
                query = query.filter(MonitorMetric.metric_name == filter.metric_name)
            if filter.start_time:
                query = query.filter(MonitorMetric.timestamp >= filter.start_time)
            if filter.end_time:
                query = query.filter(MonitorMetric.timestamp <= filter.end_time)

        return query.count()

    def get_latest_metric(self, service: str, metric_name: str) -> Optional[MonitorMetric]:
        """
        获取最新指标
        """
        return self.db.query(MonitorMetric).filter(
            MonitorMetric.service == service,
            MonitorMetric.metric_name == metric_name
        ).order_by(MonitorMetric.timestamp.desc()).first()

    def get_metric_stats(
        self,
        service: str,
        metric_name: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """
        获取指标统计信息
        """
        from sqlalchemy import func

        query = self.db.query(
            func.avg(MonitorMetric.metric_value).label('avg'),
            func.min(MonitorMetric.metric_value).label('min'),
            func.max(MonitorMetric.metric_value).label('max'),
            func.count(MonitorMetric.id).label('count')
        ).filter(
            MonitorMetric.service == service,
            MonitorMetric.metric_name == metric_name
        )

        if start_time:
            query = query.filter(MonitorMetric.timestamp >= start_time)
        if end_time:
            query = query.filter(MonitorMetric.timestamp <= end_time)

        result = query.first()

        return {
            "avg": float(result.avg) if result.avg else 0,
            "min": float(result.min) if result.min else 0,
            "max": float(result.max) if result.max else 0,
            "count": result.count
        }
