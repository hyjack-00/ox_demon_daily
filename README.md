## Ox Demon Daily 牛魔日报 🐮😈

### 推送目标

飞书 webhook 机器人（请在 config.json 中配置）


### 信息

#### 来源

- github 
- 金融与科技大新闻
- 科研新文章

#### 格式

所有 content 均使用 `data: List[Dict[str, Any]]` 格式，多个信息源之间是将 List 进行拼接。

```python 
# 例如
[
    {
        "title": "标题",
        "source": "信息源"
        "content": "内容",
    },
    ...
]

```

