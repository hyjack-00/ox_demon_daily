import requests
import json
import time
from datetime import datetime

# 飞书 Webhook 地址，替换为你自己的 Webhook 链接
WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/7a36ecf9-135e-4df6-a44f-ae5b9e51c520"

def send_text_message(content, mention_list=None, mention_all=False):
    """
    发送文本类型消息
    
    参数:
        content: 消息内容
        mention_list: 要@的用户ID列表，例如 ["user1", "user2"]
        mention_all: 是否@所有人，默认为False
    """
    payload = {
        "msg_type": "text",
        "content": {
            "text": content
        }
    }
    
    # 处理@用户逻辑
    if mention_list:
        payload["content"]["text"] = content
        payload["mentioned_users"] = mention_list
    if mention_all:
        payload["content"]["text"] = content
        payload["mentioned_all"] = True
    
    response = requests.post(WEBHOOK_URL, data=json.dumps(payload))
    return response.json()

def send_link_message(title, text, url, image_url=None):
    """
    发送链接类型消息
    
    参数:
        title: 链接标题
        text: 链接描述
        url: 点击链接跳转的地址
        image_url: 链接左侧图片地址
    """
    payload = {
        "msg_type": "interactive",
        "card": {
            "config": {
                "wide_screen_mode": True
            },
            "elements": [
                {
                    "tag": "a",
                    "text": {
                        "tag": "lark_md",
                        "content": f"[{title}]({url})"
                    },
                    "href": url
                },
                {
                    "tag": "note",
                    "elements": [
                        {
                            "tag": "plain_text",
                            "content": text
                        }
                    ]
                }
            ],
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": title
                }
            }
        }
    }
    
    # 添加图片
    if image_url:
        payload["card"]["elements"].insert(0, {
            "tag": "image",
            "image_url": image_url,
            "alt": {
                "tag": "plain_text",
                "content": title
            }
        })
    
    response = requests.post(WEBHOOK_URL, data=json.dumps(payload))
    return response.json()

def send_markdown_message(markdown_content):
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
    
    response = requests.post(WEBHOOK_URL, data=json.dumps(payload))
    return response.json()

def send_multi_card_message():
    """
    发送多条卡片组合消息
    """
    payload = {
        "msg_type": "interactive",
        "card": {
            "config": {
                "wide_screen_mode": True
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": "### 今日工作提醒\n\n- 10:00 项目进度会议\n- 14:30 客户需求沟通"
                    }
                },
                {
                    "tag": "div",
                    "elements": [
                        {
                            "tag": "button",
                            "text": {
                                "tag": "plain_text",
                                "content": "完成任务"
                            },
                            "type": "primary",
                            "value": {
                                "action": "complete"
                            }
                        },
                        {
                            "tag": "button",
                            "text": {
                                "tag": "plain_text",
                                "content": "推迟任务"
                            },
                            "type": "default",
                            "value": {
                                "action": "postpone"
                            }
                        }
                    ]
                }
            ],
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": "工作日程通知"
                },
                "template": "blue"
            }
        }
    }
    
    response = requests.post(WEBHOOK_URL, data=json.dumps(payload))
    return response.json()

# 示例使用
if __name__ == "__main__":
    # # 发送普通文本消息
    # now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # text_response = send_text_message(f"Python 自动消息测试 - {now}")
    # print("文本消息发送结果:", text_response)
    
    # 发送带@的文本消息
    send_text_message("【重要通知，请相关人员注意】哈基米来咯", mention_all=True)
    
    # # 发送链接消息
    # link_response = send_link_message(
    #     "哈基米参考资料",
    #     "关于哈基米的详细介绍和相关资料",
    #     "https://www.inter.it/en/squadra/hakimi-achraf",
    #     "https://upload.wikimedia.org/wikipedia/commons/7/7d/Achraf_Hakimi_2021.jpg"
    # )
    # print("链接消息发送结果:", link_response)
    
    # 发送Markdown消息
    markdown_content = """
    # 标题1
    ## 标题2
    - 列表项1
    - 列表项2
    [链接](https://example.com)
    """
    md_response = send_markdown_message(markdown_content)
    print("Markdown消息发送结果:", md_response)
    
    # 发送多卡片消息
    # multi_response = send_multi_card_message()
    # print("多卡片消息发送结果:", multi_response)