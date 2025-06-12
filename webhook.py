import requests
import json
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from requests.exceptions import RequestException

class Webhook:
    def __init__(self, webhook_url):
        """
        初始化 Webhook 类
        
        参数:
            webhook_url: Webhook 地址
        """
        self.webhook_url = webhook_url
        self.session = requests.Session()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=3,  # 最大重试次数
            backoff_factor=1,  # 重试间隔
            status_forcelist=[500, 502, 503, 504]  # 需要重试的HTTP状态码
        )
        
        # 配置适配器
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _make_request(self, payload):
        """
        发送请求的通用方法
        
        参数:
            payload: 请求数据
        """
        try:
            response = self.session.post(
                self.webhook_url,
                data=json.dumps(payload),
                timeout=10,  # 设置超时时间
                verify=True  # 验证SSL证书
            )
            response.raise_for_status()  # 检查响应状态
            try:
                return response.json()
            except json.JSONDecodeError:
                return {"status": response.status_code, "text": response.text}
        except RequestException as e:
            return {"status": "error", "error": str(e)}

    def send_text_message(self, content, mention_all=False):
        """
        发送文本类型消息
        
        参数:
            content: 消息内容
            mention_all: 是否@所有人，默认为False
        """
        payload = {
            "msg_type": "text",
            "content": {
                "text": content
            }
        }
        
        # 处理@所有人逻辑
        if mention_all:
            payload["content"]["text"] = content
            payload["mentioned_all"] = True
        
        return self._make_request(payload)

    def send_markdown_message(self, markdown_content):
        """
        发送Markdown格式消息
        
        参数:
            markdown_content: Markdown格式的内容
        """
        payload = {
            "msg_type": "interactive",
            "card": {
                "config": {
                    "wide_screen_mode": True
                },
                "elements": [
                    {
                        "tag": "markdown",
                        "content": markdown_content
                    }
                ],
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": "Markdown 消息"
                    }
                }
            }
        }
        
        return self._make_request(payload)

# 使用示例
if __name__ == "__main__":
    # 初始化 Webhook 实例
    webhook = Webhook("https://webhook.site/0f8f6a6f-ff45-47b3-8b22-a5422e57d47a")
    
    # 发送文本消息
    text_response = webhook.send_text_message("测试消息", mention_all=True)
    print("文本消息发送结果:", text_response)
    
    # 发送 Markdown 消息
    markdown_content = """
    # 标题1
    ## 标题2
    - 列表项1
    - 列表项2
    [链接](https://example.com)
    """
    md_response = webhook.send_markdown_message(markdown_content)
    print("Markdown消息发送结果:", md_response)