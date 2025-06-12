import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from datetime import datetime
from webhook_robot import send_markdown_message
import time

def get_github_trending(time_range: str = "daily", language: str = None) -> List[Dict]:
    """
    获取 GitHub Trending 页面的数据
    
    Args:
        time_range (str): 时间范围，可选值：daily, weekly, monthly
        language (str): 编程语言，例如：python, javascript, go 等
    
    Returns:
        List[Dict]: 包含仓库信息的列表
    """
    base_url = "https://github.com/trending"
    url = f"{base_url}/{language}" if language else base_url
    url = f"{url}?since={time_range}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        repos = []
        
        for article in soup.select('article.Box-row'):
            repo_info = {}
            
            repo_element = article.select_one('h2.h3 a')
            if repo_element:
                repo_info['name'] = repo_element.get_text(strip=True)
                repo_info['url'] = f"https://github.com{repo_element['href']}"
            
            description = article.select_one('p')
            repo_info['description'] = description.get_text(strip=True) if description else ''
            
            language_element = article.select_one('span[itemprop="programmingLanguage"]')
            repo_info['language'] = language_element.get_text(strip=True) if language_element else ''
            
            stars_element = article.select_one('a[href*="stargazers"]')
            repo_info['stars'] = stars_element.get_text(strip=True) if stars_element else '0'
            
            forks_element = article.select_one('a[href*="forks"]')
            repo_info['forks'] = forks_element.get_text(strip=True) if forks_element else '0'
            
            today_stars_element = article.select_one('span.d-inline-block.float-sm-right')
            repo_info['today_stars'] = today_stars_element.get_text(strip=True) if today_stars_element else '0'
            
            repos.append(repo_info)
        
        return repos
    
    except requests.RequestException as e:
        print(f"获取 GitHub Trending 数据时发生错误: {e}")
        return []

def format_trending_markdown(repos: List[Dict], language: str = None, time_range: str = "daily") -> str:
    """
    将仓库信息格式化为 Markdown 格式
    
    Args:
        repos (List[Dict]): 仓库信息列表
        language (str): 编程语言
        time_range (str): 时间范围
    
    Returns:
        str: Markdown 格式的消息
    """
    if not repos:
        return "暂无数据"
    
    # 转换时间范围为中文
    time_range_map = {
        "daily": "今日",
        "weekly": "本周",
        "monthly": "本月"
    }
    time_range_cn = time_range_map.get(time_range, time_range)
    
    # 构建标题
    title = f"📊 GitHub Trending {time_range_cn}榜单"
    if language:
        title += f" - {language.capitalize()}"
    
    # 构建内容
    content = f"# {title}\n\n"
    content += f"*更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
    
    for i, repo in enumerate(repos, 1):
        content += f"## {i}. [{repo['name']}]({repo['url']})\n\n"
        if repo['description']:
            content += f"{repo['description']}\n\n"
        content += f"- 💻 语言：{repo['language']}\n"
        content += f"- ⭐ 星标：{repo['stars']}\n"
        content += f"- 🔄 Fork：{repo['forks']}\n"
        content += f"- 📈 {time_range_cn}新增：{repo['today_stars']}\n\n"
        content += "---\n\n"
    
    return content

def send_trending_to_webhook(language: str = None, time_range: str = "daily"):
    """
    获取 GitHub Trending 数据并发送到 webhook
    
    Args:
        language (str): 编程语言
        time_range (str): 时间范围
    """
    repos = get_github_trending(time_range=time_range, language=language)
    markdown_content = format_trending_markdown(repos, language, time_range)
    response = send_markdown_message(markdown_content)
    return response

if __name__ == "__main__":
    # 示例：发送 Python 相关的每日 trending
    send_trending_to_webhook(language="python", time_range="daily")
    
    # 示例：发送所有语言的周榜
    # send_trending_to_webhook(time_range="weekly")
    
    # 示例：发送 JavaScript 的月榜
    # send_trending_to_webhook(language="javascript", time_range="monthly") 