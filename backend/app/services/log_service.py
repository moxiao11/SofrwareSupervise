"""
Log Service
日志服务
"""
from datetime import datetime
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any

from app.models.application_log import ApplicationLog
from app.schemas.application_log import LogCreate, LogFilter
from app.core.logging import get_logger


class LogService:
    """日志服务类"""

    def __init__(self, db: Session):
        self.db = db
        self.logger = get_logger(service="log-service")

    def create_log(
        self,
        service: str,
        level: str,
        message: str,
        trace_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ApplicationLog:
        """
        创建日志记录
        """
        log = ApplicationLog(
            timestamp=datetime.now(),
            service=service,
            level=level.upper(),
            message=message,
            trace_id=trace_id,
            metadata_json=metadata
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)

        # 同时输出到文件日志
        file_logger = get_logger(service=service, trace_id=trace_id or "-")
        if level.upper() == "ERROR":
            file_logger.error(message)
        elif level.upper() == "WARNING" or level.upper() == "WARN":
            file_logger.warning(message)
        elif level.upper() == "CRITICAL":
            file_logger.critical(message)
        else:
            file_logger.info(message)

        return log

    def get_logs(
        self,
        filter: Optional[LogFilter] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ApplicationLog]:
        """
        查询日志列表
        """
        query = self.db.query(ApplicationLog)

        if filter:
            if filter.service:
                query = query.filter(ApplicationLog.service == filter.service)
            if filter.level:
                query = query.filter(ApplicationLog.level == filter.level.upper())
            if filter.trace_id:
                query = query.filter(ApplicationLog.trace_id == filter.trace_id)
            if filter.start_time:
                query = query.filter(ApplicationLog.timestamp >= filter.start_time)
            if filter.end_time:
                query = query.filter(ApplicationLog.timestamp <= filter.end_time)
            if filter.keyword:
                query = query.filter(ApplicationLog.message.contains(filter.keyword))

        query = query.order_by(ApplicationLog.timestamp.desc())
        logs = query.offset(skip).limit(limit).all()

        return logs

    def count_logs(self, filter: Optional[LogFilter] = None) -> int:
        """
        统计日志数量
        """
        query = self.db.query(ApplicationLog)

        if filter:
            if filter.service:
                query = query.filter(ApplicationLog.service == filter.service)
            if filter.level:
                query = query.filter(ApplicationLog.level == filter.level.upper())
            if filter.trace_id:
                query = query.filter(ApplicationLog.trace_id == filter.trace_id)
            if filter.start_time:
                query = query.filter(ApplicationLog.timestamp >= filter.start_time)
            if filter.end_time:
                query = query.filter(ApplicationLog.timestamp <= filter.end_time)
            if filter.keyword:
                query = query.filter(ApplicationLog.message.contains(filter.keyword))

        return query.count()

    def get_log_by_id(self, log_id: int) -> Optional[ApplicationLog]:
        """
        根据ID获取日志
        """
        return self.db.query(ApplicationLog).filter(ApplicationLog.id == log_id).first()

    def log_slow_sql(
        self,
        service: str,
        sql: str,
        duration_ms: float,
        trace_id: Optional[str] = None
    ) -> ApplicationLog:
        """
        记录慢SQL日志
        """
        message = f"Slow SQL detected: {duration_ms:.2f}ms - {sql}"
        return self.create_log(
            service=service,
            level="WARN",
            message=message,
            trace_id=trace_id,
            metadata={"sql": sql, "duration_ms": duration_ms}
        )

    def log_error(
        self,
        service: str,
        error: str,
        trace_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ApplicationLog:
        """
        记录错误日志
        """
        return self.create_log(
            service=service,
            level="ERROR",
            message=error,
            trace_id=trace_id,
            metadata=metadata
        )

    def log_info(
        self,
        service: str,
        message: str,
        trace_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ApplicationLog:
        """
        记录信息日志
        """
        return self.create_log(
            service=service,
            level="INFO",
            message=message,
            trace_id=trace_id,
            metadata=metadata
        )
