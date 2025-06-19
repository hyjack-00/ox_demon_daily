from abc import ABC, abstractmethod
from typing import Any, Dict, List
import sys

class BaseSource(ABC):
    """信息源基类"""
    
    @abstractmethod
    def fetch_data(self, **kwargs) -> str:
        """
        获取数据并格式化为消息
        """
        pass
