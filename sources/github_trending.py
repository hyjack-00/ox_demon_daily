import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import json
from datetime import datetime
from .base import BaseSource

class GitHubTrendingSource(BaseSource):
    """GitHub Trending 信息源"""
    
    def fetch_data(self, **kwargs) -> str:
        """
        获取 GitHub Trending 数据并格式化为消息
        
        Args:
            **kwargs: 可选的参数，包括 time_range
        
        Returns:
            str: 格式化后的消息
        """
        time_range = kwargs.get('time_range', 'daily')
        repos = self._get_github_trending(time_range=time_range)
        return self._format_trending_message(repos)
    
    def _get_github_trending(self, time_range: str = "daily") -> List[Dict]:
        """
        获取 GitHub Trending 页面的数据
        
        Args:
            time_range (str): 时间范围，可选值：daily, weekly, monthly
        
        Returns:
            List[Dict]: 包含仓库信息的列表
        """
        # 构建 URL
        base_url = "https://github.com/trending"
        url = f"{base_url}?since={time_range}"
        
        # 设置请求头，模拟浏览器访问
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            repos = []
            
            # 查找所有仓库条目
            for article in soup.select('article.Box-row'):
                repo_info = {}
                
                # 获取仓库名称和链接
                repo_element = article.select_one('h2.h3 a')
                if repo_element:
                    repo_info['name'] = repo_element.get_text(strip=True)
                    repo_info['url'] = f"https://github.com{repo_element['href']}"
                
                # 获取描述
                description = article.select_one('p')
                repo_info['description'] = description.get_text(strip=True) if description else ''
                
                # 获取编程语言
                language_element = article.select_one('span[itemprop="programmingLanguage"]')
                repo_info['language'] = language_element.get_text(strip=True) if language_element else ''
                
                # 获取星标数
                stars_element = article.select_one('a[href*="stargazers"]')
                repo_info['stars'] = stars_element.get_text(strip=True) if stars_element else '0'
                
                # 获取 fork 数
                forks_element = article.select_one('a[href*="forks"]')
                repo_info['forks'] = forks_element.get_text(strip=True) if forks_element else '0'
                
                # 获取今日星标数
                today_stars_element = article.select_one('span.d-inline-block.float-sm-right')
                repo_info['today_stars'] = today_stars_element.get_text(strip=True) if today_stars_element else '0'
                
                repos.append(repo_info)
            
            return repos
        
        except requests.RequestException as e:
            print(f"获取 GitHub Trending 数据时发生错误: {e}")
            return []

    def _format_trending_message(self, repos: List[Dict]) -> str:
        """
        将仓库信息格式化为易读的消息
        
        Args:
            repos (List[Dict]): 仓库信息列表
        
        Returns:
            str: 格式化后的消息
        """
        if not repos:
            return "暂无数据"
        
        message = f"📊 GitHub Trending ({datetime.now().strftime('%Y-%m-%d')})\n\n"
        
        for i, repo in enumerate(repos, 1):
            message += f"{i}. {repo['name']}\n"
            message += f"   📝 {repo['description']}\n"
            message += f"   💻 {repo['language']}\n"
            message += f"   ⭐ {repo['stars']} | 🔄 {repo['forks']} | 📈 {repo['today_stars']}\n"
            message += f"   🔗 {repo['url']}\n\n"
        
        return message

# 创建同名信息源实例
github_trending_source = GitHubTrendingSource()