import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

class Logger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialize_logger()
        return cls._instance
    
    def _initialize_logger(self):
        """初始化日志配置"""
        self.logger = logging.getLogger('ox_demon')
        self.logger.setLevel(logging.DEBUG)
        
        # 创建日志目录
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 日志文件名格式：ox_demon_YYYY-MM-DD.log
        log_file = os.path.join(log_dir, f'ox_demon_{datetime.now().strftime("%Y-%m-%d")}.log')
        
        # 文件处理器 - DEBUG级别
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        
        # 控制台处理器 - INFO级别
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        
        # 添加处理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def debug(self, message):
        """输出调试信息到文件"""
        self.logger.debug(message)
    
    def info(self, message):
        """输出信息到控制台和文件"""
        self.logger.info(message)
    
    def warning(self, message):
        """输出警告信息到控制台和文件"""
        self.logger.warning(message)
    
    def error(self, message):
        """输出错误信息到控制台和文件"""
        self.logger.error(message)
    
    def critical(self, message):
        """输出严重错误信息到控制台和文件"""
        self.logger.critical(message)

# 创建全局日志实例
logger = Logger()

if __name__ == "__main__":
    # 测试日志功能
    logger.debug("这是一条调试信息")
    logger.info("这是一条普通信息")
    logger.warning("这是一条警告信息")
    logger.error("这是一条错误信息")
    logger.critical("这是一条严重错误信息") 