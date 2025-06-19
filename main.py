import time
import signal
import sys
import importlib
from datetime import datetime
import threading
from typing import Dict, Any, List
import pytz

from logger import logger
from config import config
from processors.base import BaseProcessor
from webhook import Webhook

def start_api_server():
    from api_server import run_api
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    logger.info("API 管理服务已在后台启动")

class OxDemonService:
    def __init__(self):
        self.running = True
        self.sources = {}  # 动态加载的信息源模块
        self.postprocessors = {}  # 动态加载的后处理器模块
        self.webhook = Webhook(config.get_webhook_url())
        self._load_modules()
        
        # 注册信号处理
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)
    
    def _handle_signal(self, signum, frame):
        """处理终止信号"""
        logger.info(f"收到信号 {signum}，准备停止服务...")
        self.running = False
        sys.exit(0)
    
    def _load_modules(self):
        """动态加载信息源和后处理器模块"""
        # 加载信息源
        for source_config in config.get_sources():
            try:
                module_name = f"sources.{source_config['name']}"
                module = importlib.import_module(module_name)
                source = getattr(module, f"{source_config['name']}_source")
                self.sources[source_config['name']] = source
                logger.info(f"成功加载信息源: {source_config['name']}")
            except Exception as e:
                logger.error(f"加载信息源 {source_config['name']} 失败: {e}")

        # 加载后处理器
        for processor_config in config.get_postprocessors():
            try:
                module_name = f"processors.{processor_config['name']}"
                module = importlib.import_module(module_name)
                processor = getattr(module, f"{processor_config['name']}_processor")
                if not isinstance(processor, BaseProcessor):
                    raise TypeError(f"处理器 {processor_config['name']} 不是 BaseProcessor 的实例")
                self.postprocessors[processor_config['name']] = processor
                logger.info(f"成功加载后处理器: {processor_config['name']}")
            except Exception as e:
                logger.error(f"加载后处理器 {processor_config['name']} 失败: {e}")
        
        # 如果没有加载任何后处理器，使用默认处理器
        if not self.postprocessors:
            try:
                from processors.default import default_processor
                self.postprocessors['default'] = default_processor
                logger.info("没有加载任何后处理器，使用默认处理器")
            except Exception as e:
                logger.error(f"加载默认处理器失败: {e}")
    
    def _reload_config(self):
        """重新加载配置和模块"""
        logger.info("重新加载配置...")
        # 重新加载配置
        importlib.reload(config)
        # 重新加载模块
        self._load_modules()
    
    def _fetch_data(self) -> List[Dict[str, Any]]:
        """从所有启用的信息源获取数据"""
        all_data = []
        for source_config in config.get_sources():
            source_name = source_config['name']
            if source_name in self.sources:
                try:
                    source_data = self.sources[source_name].get_data(**source_config['params'])
                    if source_data:
                        all_data.extend(source_data)
                        logger.info(f"从 {source_name} 获取到 {len(source_data)} 条数据")
                except Exception as e:
                    logger.error(f"从 {source_name} 获取数据失败: {e}")
        return all_data
    
    def _process_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """使用所有启用的后处理器处理数据"""
        processed_data = data
        for processor_config in config.get_postprocessors():
            processor_name = processor_config['name']
            if processor_name in self.postprocessors:
                try:
                    processed_data = self.postprocessors[processor_name].process(
                        processed_data,
                        **processor_config['params']
                    )
                    logger.info(f"使用 {processor_name} 处理数据，剩余 {len(processed_data)} 条")
                except Exception as e:
                    logger.error(f"使用 {processor_name} 处理数据失败: {e}")
        return processed_data
    
    def _send_data(self, data: List[Dict[str, Any]]):
        """发送处理后的数据"""
        if not data:
            logger.info("没有数据需要发送")
            return
        
        try:
            # 获取当前时区的时间
            tz = pytz.timezone(config.get_schedule()['timezone'])
            now = datetime.now(tz)
            
            # 这里需要根据实际的数据格式构建 markdown 消息
            markdown_content = "# 牛魔日报 🐮😈\n\n"
            markdown_content += f"*更新时间：{now.strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
            
            for item in data:
                markdown_content += f"## {item.get('title', '无标题')}\n\n"
                markdown_content += f"{item.get('content', '无内容')}\n\n"
                if 'url' in item:
                    markdown_content += f"[查看详情]({item['url']})\n\n"
                markdown_content += "---\n\n"
            
            response = self.webhook.send_markdown_message(markdown_content)
            logger.info(f"发送数据成功，共 {len(data)} 条")
        except Exception as e:
            logger.error(f"发送数据失败: {e}")
    
    def run(self):
        """运行服务"""
        logger.info("牛魔日报服务启动...")
        start_api_server()  # 启动API服务
        
        while self.running:
            try:
                # 获取下次运行时间（已经是带时区的时间）
                next_run = config.get_next_run_time()
                # 获取当前时区的时间
                tz = pytz.timezone(config.get_schedule()['timezone'])
                now = datetime.now(tz)
                
                # 计算等待时间
                wait_seconds = (next_run - now).total_seconds()
                if wait_seconds > 0:
                    logger.info(f"等待 {wait_seconds:.1f} 秒后执行下一次推送")
                    time.sleep(wait_seconds)
                    
                    # # 分段等待，再检查一次是否需要重载配置
                    # while wait_seconds > 0 and self.running:
                    #     sleep_time = min(5, wait_seconds)
                    #     time.sleep(sleep_time)
                    #     wait_seconds -= sleep_time
                
                if not self.running:
                    break
                
                # 执行推送流程
                logger.info("开始执行推送流程...")
                data = self._fetch_data()
                processed_data = self._process_data(data)
                self._send_data(processed_data)
                
            except Exception as e:
                logger.error(f"服务运行出错: {e}")
                time.sleep(1)  # 出错后等待1秒再继续
        
        logger.info("牛魔日报服务已停止")

def main():
    service = OxDemonService()
    service.run()

if __name__ == "__main__":
    main()
