from typing import List, Dict, Any
from .base import BaseProcessor

class KeywordMatchProcessor(BaseProcessor):
    """关键词匹配处理器"""
    
    def process(self, content: List[Dict[str, Any]], **kwargs) -> List[Dict[str, Any]]:
        """
        根据关键词过滤内容
        
        Args:
            content: 要处理的内容列表，每个元素是一个字典
            **kwargs: 其他参数，包括：
                - keywords: 关键词列表
                - match_all: 是否要求匹配所有关键词（默认为False，即匹配任一关键词）
                - case_sensitive: 是否区分大小写（默认为False）
        
        Returns:
            List[Dict[str, Any]]: 过滤后的内容列表
        """
        if not content:
            return []
            
        keywords = kwargs.get('keywords', [])
        if not keywords:
            return content
            
        match_all = kwargs.get('match_all', False)
        case_sensitive = kwargs.get('case_sensitive', False)
        
        # 如果不区分大小写，将关键词转换为小写
        if not case_sensitive:
            keywords = [k.lower() for k in keywords]
        
        filtered_content = []
        for item in content:
            # 获取所有文本字段
            text_fields = []
            for value in item.values():
                if isinstance(value, str):
                    text_fields.append(value)
            
            # 如果不区分大小写，将文本转换为小写
            if not case_sensitive:
                text_fields = [t.lower() for t in text_fields]
            
            # 检查是否匹配关键词
            if match_all:
                # 要求匹配所有关键词
                if all(any(k in t for t in text_fields) for k in keywords):
                    filtered_content.append(item)
            else:
                # 匹配任一关键词
                if any(any(k in t for t in text_fields) for k in keywords):
                    filtered_content.append(item)
        
        return filtered_content


# 创建同名处理器实例
keyword_match_processor = KeywordMatchProcessor() 
