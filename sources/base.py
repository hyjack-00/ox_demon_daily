from abc import ABC, abstractmethod
from typing import Any, Dict
import sys

class BaseSource(ABC):
    """信息源基类"""
    
    @abstractmethod
    def fetch_data(self, **kwargs) -> str:
        """
        获取数据并格式化为消息
        
        Args:
            **kwargs: 可选的参数
            
        Returns:
            str: 格式化后的消息
        """
        pass
