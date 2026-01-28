"""
基于Socket的机器人遥操作接口
支持TCP和UDP两种协议
"""
import socket
import json
from typing import Optional, Dict, Any
from teleop_interface import TeleopInterface


class SocketTeleopInterface(TeleopInterface):
    """Socket遥操作接口"""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 8888, 
                 protocol: str = "TCP", buffer_size: int = 4096):
        """
        初始化Socket接口
        
        Args:
            host: 服务器地址
            port: 端口号
            protocol: 协议类型，"TCP"或"UDP"
            buffer_size: 接收缓冲区大小
        """
        super().__init__()
        self.host = host
        self.port = port
        self.protocol = protocol.upper()
        self.buffer_size = buffer_size
        self.socket = None
        
        if self.protocol not in ["TCP", "UDP"]:
            raise ValueError("协议类型必须是TCP或UDP")
    
    def connect(self) -> bool:
        """建立Socket连接"""
        try:
            if self.protocol == "TCP":
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.host, self.port))
                self.logger.info(f"TCP连接成功: {self.host}:{self.port}")
            else:  # UDP
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.logger.info(f"UDP Socket创建成功: {self.host}:{self.port}")
            
            self.is_connected = True
            return True
            
        except Exception as e:
            self.logger.error(f"连接失败: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self) -> bool:
        """断开Socket连接"""
        try:
            if self.socket:
                self.socket.close()
                self.socket = None
                self.logger.info("Socket连接已断开")
            self.is_connected = False
            return True
            
        except Exception as e:
            self.logger.error(f"断开连接失败: {e}")
            return False
    
    def send_command(self, command: Dict[str, Any]) -> bool:
        """
        发送控制指令
        
        Args:
            command: 控制指令字典
            
        Returns:
            bool: 发送成功返回True
        """
        if not self.is_connected or not self.socket:
            self.logger.error("未连接，无法发送指令")
            return False
        
        try:
            # 将指令序列化为JSON
            data = json.dumps(command).encode('utf-8')
            
            if self.protocol == "TCP":
                self.socket.sendall(data)
            else:  # UDP
                self.socket.sendto(data, (self.host, self.port))
            
            self.logger.debug(f"指令已发送: {command}")
            return True
            
        except Exception as e:
            self.logger.error(f"发送指令失败: {e}")
            return False
    
    def receive_data(self, timeout: float = 1.0) -> Optional[Dict[str, Any]]:
        """
        接收机器人反馈数据
        
        Args:
            timeout: 超时时间（秒）
            
        Returns:
            Optional[Dict]: 接收到的数据字典
        """
        if not self.is_connected or not self.socket:
            self.logger.error("未连接，无法接收数据")
            return None
        
        try:
            # 设置超时时间
            self.socket.settimeout(timeout)
            
            if self.protocol == "TCP":
                data = self.socket.recv(self.buffer_size)
            else:  # UDP
                data, _ = self.socket.recvfrom(self.buffer_size)
            
            if not data:
                return None
            
            # 解析JSON数据
            result = json.loads(data.decode('utf-8'))
            self.logger.debug(f"接收到数据: {result}")
            return result
            
        except socket.timeout:
            self.logger.debug("接收数据超时")
            return None
        except Exception as e:
            self.logger.error(f"接收数据失败: {e}")
            return None


class SocketTeleopServer(TeleopInterface):
    """Socket遥操作服务器端"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8888, 
                 protocol: str = "TCP", buffer_size: int = 4096):
        """
        初始化Socket服务器
        
        Args:
            host: 监听地址
            port: 端口号
            protocol: 协议类型，"TCP"或"UDP"
            buffer_size: 接收缓冲区大小
        """
        super().__init__()
        self.host = host
        self.port = port
        self.protocol = protocol.upper()
        self.buffer_size = buffer_size
        self.server_socket = None
        self.client_socket = None
        self.client_address = None
        
        if self.protocol not in ["TCP", "UDP"]:
            raise ValueError("协议类型必须是TCP或UDP")
    
    def connect(self) -> bool:
        """启动服务器并等待客户端连接"""
        try:
            if self.protocol == "TCP":
                self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.server_socket.bind((self.host, self.port))
                self.server_socket.listen(1)
                self.logger.info(f"TCP服务器监听中: {self.host}:{self.port}")
                
                # 等待客户端连接
                self.client_socket, self.client_address = self.server_socket.accept()
                self.logger.info(f"客户端已连接: {self.client_address}")
                
            else:  # UDP
                self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.server_socket.bind((self.host, self.port))
                self.logger.info(f"UDP服务器启动: {self.host}:{self.port}")
            
            self.is_connected = True
            return True
            
        except Exception as e:
            self.logger.error(f"服务器启动失败: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self) -> bool:
        """断开连接并关闭服务器"""
        try:
            if self.client_socket:
                self.client_socket.close()
                self.client_socket = None
            if self.server_socket:
                self.server_socket.close()
                self.server_socket = None
            self.logger.info("服务器已关闭")
            self.is_connected = False
            return True
            
        except Exception as e:
            self.logger.error(f"关闭服务器失败: {e}")
            return False
    
    def send_command(self, command: Dict[str, Any]) -> bool:
        """发送数据到客户端"""
        if not self.is_connected:
            self.logger.error("服务器未启动")
            return False
        
        try:
            data = json.dumps(command).encode('utf-8')
            
            if self.protocol == "TCP":
                if not self.client_socket:
                    self.logger.error("没有连接的客户端")
                    return False
                self.client_socket.sendall(data)
            else:  # UDP
                if not self.client_address:
                    self.logger.error("没有客户端地址")
                    return False
                self.server_socket.sendto(data, self.client_address)
            
            self.logger.debug(f"数据已发送: {command}")
            return True
            
        except Exception as e:
            self.logger.error(f"发送数据失败: {e}")
            return False
    
    def receive_data(self, timeout: float = 1.0) -> Optional[Dict[str, Any]]:
        """接收客户端数据"""
        if not self.is_connected:
            self.logger.error("服务器未启动")
            return None
        
        try:
            if self.protocol == "TCP":
                if not self.client_socket:
                    self.logger.error("没有连接的客户端")
                    return None
                self.client_socket.settimeout(timeout)
                data = self.client_socket.recv(self.buffer_size)
            else:  # UDP
                self.server_socket.settimeout(timeout)
                data, self.client_address = self.server_socket.recvfrom(self.buffer_size)
            
            if not data:
                return None
            
            result = json.loads(data.decode('utf-8'))
            self.logger.debug(f"接收到数据: {result}")
            return result
            
        except socket.timeout:
            self.logger.debug("接收数据超时")
            return None
        except Exception as e:
            self.logger.error(f"接收数据失败: {e}")
            return None
