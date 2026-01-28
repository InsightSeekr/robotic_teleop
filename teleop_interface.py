"""
机器人遥操作接口基类
定义了遥操作接口的标准方法
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TeleopInterface(ABC):
    """遥操作接口抽象基类"""
    
    def __init__(self):
        self.is_connected = False
        self.logger = logger
    
    @abstractmethod
    def connect(self) -> bool:
        """
        建立连接
        
        Returns:
            bool: 连接成功返回True，否则返回False
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """
        断开连接
        
        Returns:
            bool: 断开成功返回True，否则返回False
        """
        pass
    
    @abstractmethod
    def send_command(self, command: Dict[str, Any]) -> bool:
        """
        发送控制指令
        
        Args:
            command: 控制指令字典，包含机器人控制参数
            
        Returns:
            bool: 发送成功返回True，否则返回False
        """
        pass
    
    @abstractmethod
    def receive_data(self, timeout: float = 1.0) -> Optional[Dict[str, Any]]:
        """
        接收机器人反馈数据
        
        Args:
            timeout: 超时时间（秒）
            
        Returns:
            Optional[Dict]: 接收到的数据字典，失败返回None
        """
        pass
    
    def check_connection(self) -> bool:
        """
        检查连接状态
        
        Returns:
            bool: 连接正常返回True，否则返回False
        """
        return self.is_connected
