-- SmartOps Seed Data
-- 智维系统测试数据

SET NAMES utf8mb4;

-- ============================================
-- 插入测试用户
-- ============================================
INSERT INTO `users` (`username`, `password_hash`, `email`, `role`) VALUES
('admin', '$2b$12$LQv3c1yqBo9SkvXS8QJnQe', 'admin@smartops.com', 'admin'),
('ops', '$2b$12$LQv3c1yqBo9SkvXS8QJnQe', 'ops@smartops.com', 'operator'),
('dev', '$2b$12$LQv3c1yqBo9SkvXS8QJnQe', 'dev@smartops.com', 'developer');

-- ============================================
-- 插入测试服务
-- ============================================
INSERT INTO `services` (`service_name`, `service_type`, `status`, `host`, `port`) VALUES
('gateway', 'gateway', 'healthy', 'localhost', 8080),
('user-service', 'application', 'healthy', 'localhost', 8081),
('order-service', 'application', 'healthy', 'localhost', 8082),
('mysql', 'database', 'healthy', 'localhost', 3306),
('redis', 'cache', 'healthy', 'localhost', 6379);

-- ============================================
-- 插入示例日志
-- ============================================
INSERT INTO `application_logs` (`timestamp`, `service`, `level`, `message`, `trace_id`) VALUES
('2026-09-07 10:00:00', 'gateway', 'INFO', 'Gateway started successfully', 'trace-001'),
('2026-09-07 10:00:01', 'order-service', 'INFO', 'Order service initialized', 'trace-002'),
('2026-09-07 10:05:23', 'order-service', 'WARN', 'Slow query detected: 2340ms', 'trace-003'),
('2026-09-07 10:05:25', 'order-service', 'ERROR', 'Database connection timeout', 'trace-004');

-- ============================================
-- 插入示例监控指标
-- ============================================
INSERT INTO `monitor_metrics` (`service`, `metric_name`, `metric_value`, `unit`, `timestamp`) VALUES
('order-service', 'cpu_usage', 45.2, 'percent', '2026-09-07 10:00:00'),
('order-service', 'memory_usage', 62.5, 'percent', '2026-09-07 10:00:00'),
('order-service', 'latency', 120, 'ms', '2026-09-07 10:00:00'),
('order-service', 'latency', 4210, 'ms', '2026-09-07 10:05:23'),
('mysql', 'connections', 95, 'count', '2026-09-07 10:05:23');

-- ============================================
-- 插入示例告警
-- ============================================
INSERT INTO `alerts` (`service`, `alert_type`, `severity`, `message`, `status`, `metric_value`, `threshold`) VALUES
('order-service', 'high_latency', 'P1', 'Order service response time exceeds threshold', 'active', 4210, 2000),
('mysql', 'high_connections', 'P1', 'Database connection pool usage too high', 'active', 95, 90);

COMMIT;
