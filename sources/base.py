from abc import ABC, abstractmethod
from typing import Any, Dict
import sys

class BaseSource(ABC):
    """信息源基类"""
    
    @abstractmethod
    def get_data(self, **kwargs) -> str:
        """
        获取数据并格式化为消息
        
        Args:
            **kwargs: 可选的参数
            
        Returns:
            str: 格式化后的消息
        """
        pass

class SourceRegistry:
    """信息源注册表"""
    
    _sources: Dict[str, BaseSource] = {}
    
    @classmethod
    def register(cls, name: str, source: BaseSource) -> None:
        """
        注册信息源
        
        Args:
            name: 信息源名称
            source: 信息源实例
        """
        cls._sources[name] = source
    
    @classmethod
    def get_source(cls, name: str) -> BaseSource:
        """
        获取信息源实例
        
        Args:
            name: 信息源名称
            
        Returns:
            BaseSource: 信息源实例
            
        Raises:
            KeyError: 如果信息源不存在
        """
        if not cls._sources:
            print("错误：没有可用的信息源")
            sys.exit(1)
            
        if name not in cls._sources:
            raise KeyError(f"信息源 '{name}' 不存在")
        return cls._sources[name]
    
    @classmethod
    def list_sources(cls) -> list:
        """
        列出所有已注册的信息源
        
        Returns:
            list: 信息源名称列表
        """
        if not cls._sources:
            print("错误：没有可用的信息源")
            sys.exit(1)
        return list(cls._sources.keys())
    
    @classmethod
    def check_sources(cls) -> None:
        """
        检查是否有可用的信息源，如果没有则终止程序
        """
        if not cls._sources:
            print("错误：没有可用的信息源")
            sys.exit(1) 