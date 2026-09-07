-- SmartOps Database Schema
-- 智维系统数据库表结构

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================
-- 用户表
-- ============================================
CREATE TABLE IF NOT EXISTS `users` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(100) NOT NULL,
  `password_hash` VARCHAR(255) NOT NULL,
  `email` VARCHAR(200) DEFAULT NULL,
  `role` VARCHAR(50) DEFAULT 'user',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 订单表
-- ============================================
CREATE TABLE IF NOT EXISTS `orders` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `user_id` BIGINT NOT NULL,
  `product_name` VARCHAR(200) NOT NULL,
  `amount` DECIMAL(10,2) NOT NULL,
  `status` VARCHAR(50) DEFAULT 'pending',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_status` (`status`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 服务信息表
-- ============================================
CREATE TABLE IF NOT EXISTS `services` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `service_name` VARCHAR(100) NOT NULL,
  `service_type` VARCHAR(50) DEFAULT 'application',
  `status` VARCHAR(20) DEFAULT 'healthy',
  `host` VARCHAR(200) DEFAULT NULL,
  `port` INT DEFAULT NULL,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_service_name` (`service_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 应用日志表
-- ============================================
CREATE TABLE IF NOT EXISTS `application_logs` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `timestamp` DATETIME NOT NULL,
  `service` VARCHAR(100) NOT NULL,
  `level` VARCHAR(20) NOT NULL,
  `message` TEXT NOT NULL,
  `trace_id` VARCHAR(100) DEFAULT NULL,
  `metadata` JSON DEFAULT NULL,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_timestamp` (`timestamp`),
  KEY `idx_service` (`service`),
  KEY `idx_level` (`level`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 监控指标表
-- ============================================
CREATE TABLE IF NOT EXISTS `monitor_metrics` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `service` VARCHAR(100) NOT NULL,
  `metric_name` VARCHAR(100) NOT NULL,
  `metric_value` DECIMAL(20,4) NOT NULL,
  `unit` VARCHAR(50) DEFAULT NULL,
  `timestamp` DATETIME NOT NULL,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_service_metric` (`service`, `metric_name`),
  KEY `idx_timestamp` (`timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 告警表
-- ============================================
CREATE TABLE IF NOT EXISTS `alerts` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `service` VARCHAR(100) NOT NULL,
  `alert_type` VARCHAR(100) NOT NULL,
  `severity` VARCHAR(20) NOT NULL,
  `message` TEXT NOT NULL,
  `status` VARCHAR(20) DEFAULT 'active',
  `metric_value` DECIMAL(20,4) DEFAULT NULL,
  `threshold` DECIMAL(20,4) DEFAULT NULL,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `resolved_at` DATETIME DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_service` (`service`),
  KEY `idx_severity` (`severity`),
  KEY `idx_status` (`status`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 故障事件表
-- ============================================
CREATE TABLE IF NOT EXISTS `fault_events` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `event_name` VARCHAR(200) NOT NULL,
  `event_type` VARCHAR(100) NOT NULL,
  `severity` VARCHAR(20) NOT NULL,
  `description` TEXT,
  `affected_services` JSON,
  `status` VARCHAR(20) DEFAULT 'open',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `resolved_at` DATETIME DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_event_type` (`event_type`),
  KEY `idx_severity` (`severity`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 诊断结果表
-- ============================================
CREATE TABLE IF NOT EXISTS `diagnosis_results` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `fault_event_id` BIGINT NOT NULL,
  `root_cause` TEXT NOT NULL,
  `confidence` DECIMAL(5,4) DEFAULT NULL,
  `evidence_chain` JSON,
  `affected_services` JSON,
  `recommendations` JSON,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_fault_event` (`fault_event_id`),
  CONSTRAINT `fk_diagnosis_fault` FOREIGN KEY (`fault_event_id`) REFERENCES `fault_events` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 知识库元数据表
-- ============================================
CREATE TABLE IF NOT EXISTS `knowledge_metadata` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `title` VARCHAR(300) NOT NULL,
  `category` VARCHAR(100) NOT NULL,
  `content` TEXT,
  `tags` JSON,
  `source` VARCHAR(300) DEFAULT NULL,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_category` (`category`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- LLM调用日志表
-- ============================================
CREATE TABLE IF NOT EXISTS `llm_call_logs` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `agent_type` VARCHAR(100) NOT NULL,
  `prompt` TEXT NOT NULL,
  `response` TEXT,
  `model_name` VARCHAR(100) NOT NULL,
  `tokens_used` INT DEFAULT NULL,
  `duration_ms` INT DEFAULT NULL,
  `status` VARCHAR(20) DEFAULT 'success',
  `error_message` TEXT,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_agent_type` (`agent_type`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS = 1;
