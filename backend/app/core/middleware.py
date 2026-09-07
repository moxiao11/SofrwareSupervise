"""
Request Logging Middleware
请求日志中间件
"""
import time
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import get_logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    请求日志中间件
    记录每个请求的：
    - 请求时间
    - 服务名称
    - 请求地址
    - HTTP状态
    - 请求耗时
    - Trace ID
    """

    async def dispatch(self, request: Request, call_next):
        # 生成唯一的Trace ID
        trace_id = str(uuid.uuid4())[:8]

        # 获取请求开始时间
        start_time = time.time()

        # 获取请求信息
        method = request.method
        path = request.url.path
        client_host = request.client.host if request.client else "unknown"

        # 创建logger
        logger = get_logger(service="gateway", trace_id=trace_id)

        # 记录请求开始
        logger.info(f"→ {method} {path} from {client_host}")

        # 处理请求
        try:
            response = await call_next(request)

            # 计算请求耗时
            duration_ms = (time.time() - start_time) * 1000

            # 获取HTTP状态码
            status_code = response.status_code

            # 根据状态码选择日志级别
            if status_code >= 500:
                logger.error(f"← {method} {path} {status_code} {duration_ms:.2f}ms")
            elif status_code >= 400:
                logger.warning(f"← {method} {path} {status_code} {duration_ms:.2f}ms")
            else:
                logger.info(f"← {method} {path} {status_code} {duration_ms:.2f}ms")

            # 添加Trace ID到响应头
            response.headers["X-Trace-ID"] = trace_id

            return response

        except Exception as e:
            # 计算请求耗时
            duration_ms = (time.time() - start_time) * 1000

            # 记录异常
            logger.error(f"← {method} {path} ERROR {duration_ms:.2f}ms - {str(e)}")
            raise
