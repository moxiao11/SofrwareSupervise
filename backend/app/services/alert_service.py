"""
Alert Service
告警服务 - 告警生成和管理
"""
from datetime import datetime
from sqlalchemy.orm import Session
from typing import Optional, List
from decimal import Decimal

from app.models.alert import Alert
from app.schemas.alert import AlertCreate, AlertFilter
from app.services.alert_engine import AlertRuleEngine
from app.core.logging import get_logger


class AlertService:
    """告警服务类"""

    def __init__(self, db: Session):
        self.db = db
        self.logger = get_logger(service="alert-service")
        self.rule_engine = AlertRuleEngine()

    def create_alert(
        self,
        service: str,
        alert_type: str,
        severity: str,
        message: str,
        metric_value: Optional[Decimal] = None,
        threshold: Optional[Decimal] = None
    ) -> Alert:
        """
        创建告警记录
        """
        alert = Alert(
            service=service,
            alert_type=alert_type,
            severity=severity,
            message=message,
            status='active',
            metric_value=metric_value,
            threshold=threshold
        )
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)

        self.logger.warning(f"Alert created: [{severity}] {service} - {message}")

        return alert

    def create_alerts_from_engine(self, service: str, metrics: dict) -> List[Alert]:
        """
        使用规则引擎检查指标并创建告警
        """
        triggered = self.rule_engine.check_metrics(service, metrics)
        alerts = []

        for alert_data in triggered:
            alert = self.create_alert(
                service=alert_data["service"],
                alert_type=alert_data["alert_type"],
                severity=alert_data["severity"],
                message=alert_data["message"],
                metric_value=alert_data["metric_value"],
                threshold=alert_data["threshold"]
            )
            alerts.append(alert)

        return alerts

    def resolve_alert(self, alert_id: int) -> Optional[Alert]:
        """
        解决告警
        """
        alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
        if alert:
            alert.status = 'resolved'
            alert.resolved_at = datetime.now()
            self.db.commit()
            self.db.refresh(alert)
            self.logger.info(f"Alert resolved: {alert_id}")
        return alert

    def resolve_alerts_by_service(self, service: str) -> int:
        """
        解决指定服务的所有活跃告警
        """
        alerts = self.db.query(Alert).filter(
            Alert.service == service,
            Alert.status == 'active'
        ).all()

        count = 0
        for alert in alerts:
            alert.status = 'resolved'
            alert.resolved_at = datetime.now()
            count += 1

        self.db.commit()
        self.logger.info(f"Resolved {count} alerts for {service}")
        return count

    def get_alerts(
        self,
        filter: Optional[AlertFilter] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Alert]:
        """
        查询告警列表
        """
        query = self.db.query(Alert)

        if filter:
            if filter.service:
                query = query.filter(Alert.service == filter.service)
            if filter.severity:
                query = query.filter(Alert.severity == filter.severity)
            if filter.status:
                query = query.filter(Alert.status == filter.status)
            if filter.alert_type:
                query = query.filter(Alert.alert_type == filter.alert_type)
            if filter.start_time:
                query = query.filter(Alert.created_at >= filter.start_time)
            if filter.end_time:
                query = query.filter(Alert.created_at <= filter.end_time)

        query = query.order_by(Alert.created_at.desc())
        alerts = query.offset(skip).limit(limit).all()

        return alerts

    def count_alerts(self, filter: Optional[AlertFilter] = None) -> int:
        """
        统计告警数量
        """
        query = self.db.query(Alert)

        if filter:
            if filter.service:
                query = query.filter(Alert.service == filter.service)
            if filter.severity:
                query = query.filter(Alert.severity == filter.severity)
            if filter.status:
                query = query.filter(Alert.status == filter.status)
            if filter.alert_type:
                query = query.filter(Alert.alert_type == filter.alert_type)
            if filter.start_time:
                query = query.filter(Alert.created_at >= filter.start_time)
            if filter.end_time:
                query = query.filter(Alert.created_at <= filter.end_time)

        return query.count()

    def get_alert_by_id(self, alert_id: int) -> Optional[Alert]:
        """
        根据ID获取告警
        """
        return self.db.query(Alert).filter(Alert.id == alert_id).first()

    def get_alert_stats(self) -> dict:
        """
        获取告警统计信息
        """
        total = self.count_alerts()
        active = self.count_alerts(filter=AlertFilter(status='active'))
        resolved = self.count_alerts(filter=AlertFilter(status='resolved'))

        # 按严重程度统计
        by_severity = {}
        for severity in ['P0', 'P1', 'P2', 'P3']:
            count = self.count_alerts(filter=AlertFilter(severity=severity))
            by_severity[severity] = count

        return {
            "total": total,
            "active": active,
            "resolved": resolved,
            "by_severity": by_severity
        }

    def get_active_alerts(self, service: Optional[str] = None) -> List[Alert]:
        """
        获取活跃告警
        """
        filter = AlertFilter(status='active')
        if service:
            filter.service = service
        return self.get_alerts(filter=filter)

    def check_and_create_alerts(self, service: str, metrics: dict) -> List[Alert]:
        """
        检查指标并创建告警（如果触发）
        """
        return self.create_alerts_from_engine(service, metrics)
