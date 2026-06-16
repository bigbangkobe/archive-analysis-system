-- 初始化OrangeHRM数据库

-- 创建档案分析表
CREATE TABLE IF NOT EXISTS `oovc_employee_archive_analysis` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `employee_id` INT,
  `archive_name` VARCHAR(255) NOT NULL,
  `ocr_text` LONGTEXT,
  `analysis_report` LONGTEXT,
  `confidence` DECIMAL(3, 2) DEFAULT 0.00,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_employee (employee_id),
  INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 创建档案表
CREATE TABLE IF NOT EXISTS `oovc_employee_archives` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `employee_id` INT,
  `file_name` VARCHAR(255) NOT NULL,
  `file_path` VARCHAR(500),
  `file_type` VARCHAR(50),
  `file_size` BIGINT,
  `upload_date` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `status` VARCHAR(50) DEFAULT 'uploaded',
  `notes` TEXT,
  INDEX idx_employee (employee_id),
  INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 创建分析任务表
CREATE TABLE IF NOT EXISTS `oovc_analysis_tasks` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `task_name` VARCHAR(255) NOT NULL,
  `archive_ids` TEXT,
  `status` VARCHAR(50) DEFAULT 'pending',
  `progress` INT DEFAULT 0,
  `total` INT DEFAULT 0,
  `started_at` TIMESTAMP,
  `completed_at` TIMESTAMP,
  `created_by` INT,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_status (status),
  INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 添加必要的OrangeHRM表字段
ALTER TABLE `oovc_employee` ADD COLUMN IF NOT EXISTS `archive_notes` TEXT;

-- 创建日志表
CREATE TABLE IF NOT EXISTS `oovc_system_logs` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `action` VARCHAR(255),
  `user_id` INT,
  `archive_id` INT,
  `details` TEXT,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_user (user_id),
  INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 创建系统配置表
CREATE TABLE IF NOT EXISTS `oovc_system_config` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `config_key` VARCHAR(255) UNIQUE,
  `config_value` TEXT,
  `description` VARCHAR(500),
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 插入默认配置
INSERT INTO `oovc_system_config` (`config_key`, `config_value`, `description`) VALUES
('ocr_service_url', 'http://ocr_service:8000', 'OCR服务地址'),
('llm_service_url', 'http://llm_service:11434', '大模型服务地址'),
('analysis_service_url', 'http://analysis_service:8000', '分析服务地址'),
('system_version', '1.0.0', '系统版本'),
('system_name', '档案管理分析系统', '系统名称')
ON DUPLICATE KEY UPDATE config_value=VALUES(config_value);

-- 创建权限相关表
CREATE TABLE IF NOT EXISTS `oovc_archive_permissions` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT,
  `permission_type` VARCHAR(50),
  `archive_id` INT,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 创建报告表
CREATE TABLE IF NOT EXISTS `oovc_analysis_reports` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `analysis_id` INT,
  `report_title` VARCHAR(255),
  `report_content` LONGTEXT,
  `report_format` VARCHAR(50),
  `file_path` VARCHAR(500),
  `created_by` INT,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_analysis (analysis_id),
  INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 创建索引以优化查询性能
CREATE INDEX IF NOT EXISTS idx_archive_created ON `oovc_employee_archives`(upload_date);
CREATE INDEX IF NOT EXISTS idx_analysis_created ON `oovc_employee_archive_analysis`(created_at);
