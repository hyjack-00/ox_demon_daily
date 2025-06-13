from .base import BaseProcessor

class DefaultProcessor(BaseProcessor):
    """默认后处理器，不进行任何操作"""
    
    def process(self, content: str, **kwargs) -> str:
        """
        不进行任何处理，直接返回原内容
        
        Args:
            content: 要处理的内容
            **kwargs: 其他参数
            
        Returns:
            str: 原内容
        """
        return content


# 创建默认处理器实例
default_processor = DefaultProcessor() 