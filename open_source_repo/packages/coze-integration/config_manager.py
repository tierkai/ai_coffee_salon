"""
配置管理器
负责系统配置的加载、验证和管理
"""
import os
import json
import yaml
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class CozeConfig:
    """Coze平台配置"""
    base_url: str = "https://api.coze.cn"
    api_version: str = "v3"
    timeout: int = 30
    max_retries: int = 3
    rate_limit: int = 1000  # QPS/小时
    jwt_algorithm: str = "RS256"
    jwt_expiry: int = 3600  # 1小时
    access_token_expiry: int = 86400  # 24小时


@dataclass
class DatabaseConfig:
    """数据库配置"""
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = ""
    mysql_database: str = "coffee_salon"
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = ""
    redis_db: int = 0


@dataclass
class MessageQueueConfig:
    """消息队列配置"""
    rocketmq_endpoint: str = "localhost:9876"
    rocketmq_access_key: str = ""
    rocketmq_secret_key: str = ""
    rocketmq_instance: str = "MQ_INST_xxx"
    topics: List[str] = None
    
    def __post_init__(self):
        if self.topics is None:
            self.topics = [
                "coffee.salon.knowledge.update",
                "coffee.salon.rag.completed", 
                "coffee.salon.review.approved",
                "coffee.salon.print.completed",
                "coffee.salon.auth.login"
            ]


@dataclass
class SecurityConfig:
    """安全配置"""
    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expiry: int = 3600
    encryption_key: str = ""
    audit_enabled: bool = True
    audit_retention_days: int = 365


@dataclass
class MonitoringConfig:
    """监控配置"""
    observability_enabled: bool = True
    metrics_endpoint: str = "/metrics"
    tracing_enabled: bool = True
    log_level: str = "INFO"
    structured_logging: bool = True


@dataclass
class SystemConfig:
    """系统配置"""
    coze: CozeConfig
    database: DatabaseConfig
    message_queue: MessageQueueConfig
    security: SecurityConfig
    monitoring: MonitoringConfig
    environment: str = "development"
    debug: bool = False


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.getenv("COZE_CONFIG_PATH", "config.yaml")
        self.config: Optional[SystemConfig] = None
        self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        try:
            config_file = Path(self.config_path)
            
            if config_file.exists():
                logger.info(f"加载配置文件: {config_file}")
                with open(config_file, 'r', encoding='utf-8') as f:
                    if config_file.suffix.lower() == '.json':
                        config_data = json.load(f)
                    else:
                        config_data = yaml.safe_load(f)
                
                self.config = self._parse_config(config_data)
            else:
                logger.warning(f"配置文件不存在，使用默认配置: {config_file}")
                self.config = self._get_default_config()
                
            self._validate_config()
            logger.info("配置加载完成")
            
        except Exception as e:
            logger.error(f"配置加载失败: {e}")
            raise
    
    def _parse_config(self, config_data: Dict[str, Any]) -> SystemConfig:
        """解析配置数据"""
        return SystemConfig(
            coze=CozeConfig(**config_data.get('coze', {})),
            database=DatabaseConfig(**config_data.get('database', {})),
            message_queue=MessageQueueConfig(**config_data.get('message_queue', {})),
            security=SecurityConfig(**config_data.get('security', {})),
            monitoring=MonitoringConfig(**config_data.get('monitoring', {})),
            environment=config_data.get('environment', 'development'),
            debug=config_data.get('debug', False)
        )
    
    def _get_default_config(self) -> SystemConfig:
        """获取默认配置"""
        return SystemConfig(
            coze=CozeConfig(),
            database=DatabaseConfig(),
            message_queue=MessageQueueConfig(),
            security=SecurityConfig(),
            monitoring=MonitoringConfig()
        )
    
    def _validate_config(self):
        """验证配置"""
        if not self.config:
            raise ValueError("配置为空")
        
        # 验证必要字段
        if not self.config.coze.base_url:
            raise ValueError("Coze基础URL不能为空")
        
        if not self.config.security.jwt_secret_key:
            logger.warning("JWT密钥未配置，使用默认值")
        
        # 验证环境变量覆盖
        self._load_env_overrides()
    
    def _load_env_overrides(self):
        """加载环境变量覆盖"""
        env_mappings = {
            'COZE_BASE_URL': ('coze', 'base_url'),
            'COZE_API_KEY': ('security', 'jwt_secret_key'),
            'MYSQL_HOST': ('database', 'mysql_host'),
            'MYSQL_USER': ('database', 'mysql_user'),
            'MYSQL_PASSWORD': ('database', 'mysql_password'),
            'REDIS_HOST': ('database', 'redis_host'),
            'ROCKETMQ_ENDPOINT': ('message_queue', 'rocketmq_endpoint'),
        }
        
        for env_key, (section, field) in env_mappings.items():
            env_value = os.getenv(env_key)
            if env_value:
                config_section = getattr(self.config, section)
                setattr(config_section, field, env_value)
                logger.info(f"环境变量覆盖: {env_key} -> {section}.{field}")
    
    def get_config(self) -> SystemConfig:
        """获取配置"""
        if not self.config:
            raise RuntimeError("配置未加载")
        return self.config
    
    def save_config(self, config_path: Optional[str] = None):
        """保存配置到文件"""
        if not self.config:
            raise RuntimeError("配置为空")
        
        save_path = Path(config_path or self.config_path)
        config_dict = asdict(self.config)
        
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                if save_path.suffix.lower() == '.json':
                    json.dump(config_dict, f, indent=2, ensure_ascii=False)
                else:
                    yaml.dump(config_dict, f, indent=2, allow_unicode=True)
            
            logger.info(f"配置已保存到: {save_path}")
            
        except Exception as e:
            logger.error(f"配置保存失败: {e}")
            raise
    
    def reload_config(self):
        """重新加载配置"""
        logger.info("重新加载配置")
        self._load_config()
    
    def get_coze_config(self) -> CozeConfig:
        """获取Coze配置"""
        return self.get_config().coze
    
    def get_database_config(self) -> DatabaseConfig:
        """获取数据库配置"""
        return self.get_config().database
    
    def get_message_queue_config(self) -> MessageQueueConfig:
        """获取消息队列配置"""
        return self.get_config().message_queue
    
    def get_security_config(self) -> SecurityConfig:
        """获取安全配置"""
        return self.get_config().security
    
    def get_monitoring_config(self) -> MonitoringConfig:
        """获取监控配置"""
        return self.get_config().monitoring
    
    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.get_config().environment.lower() == 'production'
    
    def is_debug(self) -> bool:
        """是否为调试模式"""
        return self.get_config().debug
    
    def get_log_level(self) -> str:
        """获取日志级别"""
        return self.get_monitoring_config().log_level


# 全局配置管理器实例
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """获取全局配置管理器实例"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_config() -> SystemConfig:
    """获取系统配置"""
    return get_config_manager().get_config()