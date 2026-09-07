"""
Alert Rule Engine
告警规则引擎 - 基于规则的异常检测
"""
from typing import List, Optional
from decimal import Decimal
from app.core.logging import get_logger


class AlertRule:
    """告警规则"""

    def __init__(
        self,
        rule_name: str,
        metric_name: str,
        operator: str,  # '>', '<', '>=', '<=', '=='
        threshold: float,
        severity: str,  # P0, P1, P2, P3
        alert_type: str,
        message_template: str
    ):
        self.rule_name = rule_name
        self.metric_name = metric_name
        self.operator = operator
        self.threshold = threshold
        self.severity = severity
        self.alert_type = alert_type
        self.message_template = message_template

    def check(self, value: float) -> bool:
        """检查是否触发告警"""
        if self.operator == '>':
            return value > self.threshold
        elif self.operator == '<':
            return value < self.threshold
        elif self.operator == '>=':
            return value >= self.threshold
        elif self.operator == '<=':
            return value <= self.threshold
        elif self.operator == '==':
            return value == self.threshold
        return False

    def generate_message(self, service: str, value: float) -> str:
        """生成告警消息"""
        return self.message_template.format(
            service=service,
            value=value,
            threshold=self.threshold
        )


class AlertRuleEngine:
    """告警规则引擎"""

    def __init__(self):
        self.logger = get_logger(service="alert-engine")
        self.rules: List[AlertRule] = []
        self._init_default_rules()

    def _init_default_rules(self):
        """初始化默认告警规则"""
        # CPU使用率告警
        self.rules.append(AlertRule(
            rule_name="high_cpu",
            metric_name="cpu_usage",
            operator=">",
            threshold=85.0,
            severity="P2",
            alert_type="high_cpu",
            message_template="{service} CPU使用率过高：{value}%（阈值：{threshold}%）"
        ))

        self.rules.append(AlertRule(
            rule_name="critical_cpu",
            metric_name="cpu_usage",
            operator=">",
            threshold=95.0,
            severity="P1",
            alert_type="critical_cpu",
            message_template="{service} CPU使用率严重过高：{value}%（阈值：{threshold}%）"
        ))

        # 内存使用率告警
        self.rules.append(AlertRule(
            rule_name="high_memory",
            metric_name="memory_usage",
            operator=">",
            threshold=90.0,
            severity="P2",
            alert_type="high_memory",
            message_template="{service} 内存使用率过高：{value}%（阈值：{threshold}%）"
        ))

        self.rules.append(AlertRule(
            rule_name="critical_memory",
            metric_name="memory_usage",
            operator=">",
            threshold=95.0,
            severity="P1",
            alert_type="critical_memory",
            message_template="{service} 内存使用率严重过高：{value}%（阈值：{threshold}%）"
        ))

        # API延迟告警
        self.rules.append(AlertRule(
            rule_name="high_latency",
            metric_name="api_latency",
            operator=">",
            threshold=2000.0,
            severity="P1",
            alert_type="high_latency",
            message_template="{service} API延迟过高：{value}ms（阈值：{threshold}ms）"
        ))

        self.rules.append(AlertRule(
            rule_name="critical_latency",
            metric_name="api_latency",
            operator=">",
            threshold=5000.0,
            severity="P0",
            alert_type="critical_latency",
            message_template="{service} API延迟严重过高：{value}ms（阈值：{threshold}ms）"
        ))

        # 数据库查询时间告警
        self.rules.append(AlertRule(
            rule_name="slow_query",
            metric_name="db_query_time",
            operator=">",
            threshold=2000.0,
            severity="P1",
            alert_type="slow_query",
            message_template="{service} 数据库查询缓慢：{value}ms（阈值：{threshold}ms）"
        ))

        self.rules.append(AlertRule(
            rule_name="critical_slow_query",
            metric_name="db_query_time",
            operator=">",
            threshold=5000.0,
            severity="P0",
            alert_type="critical_slow_query",
            message_template="{service} 数据库查询严重缓慢：{value}ms（阈值：{threshold}ms）"
        ))

        # HTTP错误率告警
        self.rules.append(AlertRule(
            rule_name="high_error_rate",
            metric_name="error_rate",
            operator=">",
            threshold=10.0,
            severity="P1",
            alert_type="high_error_rate",
            message_template="{service} HTTP错误率过高：{value}%（阈值：{threshold}%）"
        ))

        # 磁盘使用率告警
        self.rules.append(AlertRule(
            rule_name="high_disk",
            metric_name="disk_usage",
            operator=">",
            threshold=90.0,
            severity="P2",
            alert_type="high_disk",
            message_template="{service} 磁盘使用率过高：{value}%（阈值：{threshold}%）"
        ))

        self.logger.info(f"Initialized {len(self.rules)} alert rules")

    def check_metrics(self, service: str, metrics: dict) -> List[dict]:
        """
        检查指标是否触发告警

        Args:
            service: 服务名称
            metrics: 指标字典，如 {"cpu_usage": 85.5, "memory_usage": 70.0}

        Returns:
            触发的告警列表
        """
        triggered_alerts = []

        for rule in self.rules:
            metric_name = rule.metric_name
            if metric_name in metrics:
                value = float(metrics[metric_name])
                if rule.check(value):
                    alert = {
                        "service": service,
                        "alert_type": rule.alert_type,
                        "severity": rule.severity,
                        "message": rule.generate_message(service, value),
                        "metric_value": Decimal(str(value)),
                        "threshold": Decimal(str(rule.threshold)),
                        "rule_name": rule.rule_name
                    }
                    triggered_alerts.append(alert)
                    self.logger.warning(f"Alert triggered: {alert['message']}")

        return triggered_alerts

    def add_rule(self, rule: AlertRule):
        """添加自定义告警规则"""
        self.rules.append(rule)
        self.logger.info(f"Added custom alert rule: {rule.rule_name}")

    def get_rules(self) -> List[dict]:
        """获取所有告警规则"""
        return [
            {
                "rule_name": rule.rule_name,
                "metric_name": rule.metric_name,
                "operator": rule.operator,
                "threshold": rule.threshold,
                "severity": rule.severity,
                "alert_type": rule.alert_type
            }
            for rule in self.rules
        ]
