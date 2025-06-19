from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseProcessor(ABC):
    """后处理器基类"""
    
    @abstractmethod
    def process(self, content: str, **kwargs) -> str:
        """
        处理内容
        
        Args:
            content: 要处理的内容
            **kwargs: 其他参数
            
        Returns:
            str: 处理后的内容
        """
        return content

