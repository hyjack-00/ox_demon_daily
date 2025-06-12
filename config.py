import json
import os
from datetime import datetime, timedelta
import pytz
from typing import Dict, Any, List
from logger import logger

class Config:
    _instance = None
    _config_file = 'config.json'
    _default_config = {
        "webhook_url": "",
        "sources": [],
        "postprocessors": [],
        "schedule": {
            "interval_minutes": 1440,  # 默认每天
            "timezone": "Asia/Shanghai"
        }
    }
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self._config_file):
                with open(self._config_file, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
                logger.info(f"成功加载配置文件: {self._config_file}")
            else:
                self._config = self._default_config.copy()
                self._save_config()
                logger.info(f"配置文件不存在，已创建默认配置: {self._config_file}")
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            self._config = self._default_config.copy()
    
    def _save_config(self):
        """保存配置到文件"""
        try:
            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, ensure_ascii=False, indent=2)
            logger.info(f"配置已保存到: {self._config_file}")
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")
    
    def get_config(self) -> Dict[str, Any]:
        """获取完整配置"""
        return self._config
    
    def get_webhook_url(self) -> str:
        """获取 webhook URL"""
        return self._config.get('webhook_url', '')
    
    def get_sources(self) -> List[Dict[str, Any]]:
        """获取所有启用的信息源配置"""
        return [s for s in self._config.get('sources', []) if s.get('enabled', True)]
    
    def get_postprocessors(self) -> List[Dict[str, Any]]:
        """获取所有启用的后处理器配置"""
        return [p for p in self._config.get('postprocessors', []) if p.get('enabled', True)]
    
    def get_schedule(self) -> Dict[str, Any]:
        """获取调度配置"""
        return self._config.get('schedule', {})
    
    def update_source_status(self, source_name: str, enabled: bool) -> bool:
        """更新信息源启用状态"""
        for source in self._config.get('sources', []):
            if source['name'] == source_name:
                source['enabled'] = enabled
                self._save_config()
                logger.info(f"信息源 {source_name} 状态已更新为: {'启用' if enabled else '禁用'}")
                return True
        logger.warning(f"未找到信息源: {source_name}")
        return False
    
    def update_postprocessor_status(self, processor_name: str, enabled: bool) -> bool:
        """更新后处理器启用状态"""
        for processor in self._config.get('postprocessors', []):
            if processor['name'] == processor_name:
                processor['enabled'] = enabled
                self._save_config()
                logger.info(f"后处理器 {processor_name} 状态已更新为: {'启用' if enabled else '禁用'}")
                return True
        logger.warning(f"未找到后处理器: {processor_name}")
        return False
    
    def update_interval(self, minutes: int) -> bool:
        """更新推送间隔"""
        if minutes <= 0:
            logger.error("推送间隔必须大于0分钟")
            return False
        self._config['schedule']['interval_minutes'] = minutes
        self._save_config()
        logger.info(f"推送间隔已更新为: {minutes} 分钟")
        return True
    
    def get_next_run_time(self) -> datetime:
        """计算下次运行时间（时间对齐）"""
        tz = pytz.timezone(self._config['schedule']['timezone'])
        now = datetime.now(tz)
        interval = self._config['schedule']['interval_minutes']
        
        # 计算下一个时间点
        if interval >= 1440:  # 每天
            next_run = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        else:  # 按分钟间隔
            minutes = now.hour * 60 + now.minute
            next_interval = ((minutes // interval) + 1) * interval
            next_run = now.replace(hour=next_interval // 60, 
                                 minute=next_interval % 60,
                                 second=0,
                                 microsecond=0)
            if next_run <= now:
                next_run += timedelta(minutes=interval)
        
        logger.info(f"下次运行时间: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        return next_run

# 创建全局配置实例
config = Config()

if __name__ == "__main__":
    # 测试配置功能
    print("当前配置:", config.get_config())
    print("启用的信息源:", config.get_sources())
    print("启用的后处理器:", config.get_postprocessors())
    print("下次运行时间:", config.get_next_run_time()) 