"""
基于串口的机器人遥操作接口
支持RS232、RS485等串口通信
"""
import serial
import json
import time
from typing import Optional, Dict, Any, List
from teleop_interface import TeleopInterface


class SerialTeleopInterface(TeleopInterface):
    """串口遥操作接口"""
    
    def __init__(self, port: str = "/dev/ttyUSB0", baudrate: int = 115200,
                 timeout: float = 1.0, bytesize: int = 8, parity: str = 'N',
                 stopbits: int = 1):
        """
        初始化串口接口
        
        Args:
            port: 串口设备路径 (Linux: /dev/ttyUSB0, Windows: COM1)
            baudrate: 波特率 (9600, 19200, 38400, 57600, 115200等)
            timeout: 读取超时时间（秒）
            bytesize: 数据位 (5, 6, 7, 8)
            parity: 校验位 ('N':无, 'E':偶, 'O':奇, 'M':标记, 'S':空格)
            stopbits: 停止位 (1, 1.5, 2)
        """
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.serial_port = None
        
    def connect(self) -> bool:
        """打开串口连接"""
        try:
            self.serial_port = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=self.bytesize,
                parity=self.parity,
                stopbits=self.stopbits,
                timeout=self.timeout
            )
            
            # 清空缓冲区
            self.serial_port.reset_input_buffer()
            self.serial_port.reset_output_buffer()
            
            self.is_connected = True
            self.logger.info(f"串口已打开: {self.port} @ {self.baudrate}bps")
            return True
            
        except serial.SerialException as e:
            self.logger.error(f"打开串口失败: {e}")
            self.is_connected = False
            return False
        except Exception as e:
            self.logger.error(f"串口初始化失败: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self) -> bool:
        """关闭串口连接"""
        try:
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
                self.logger.info(f"串口已关闭: {self.port}")
            self.is_connected = False
            return True
            
        except Exception as e:
            self.logger.error(f"关闭串口失败: {e}")
            return False
    
    def send_command(self, command: Dict[str, Any]) -> bool:
        """
        发送控制指令
        
        Args:
            command: 控制指令字典
            
        Returns:
            bool: 发送成功返回True
        """
        if not self.is_connected or not self.serial_port or not self.serial_port.is_open:
            self.logger.error("串口未打开，无法发送指令")
            return False
        
        try:
            # 将指令序列化为JSON，并添加换行符作为结束标记
            data = (json.dumps(command) + '\n').encode('utf-8')
            
            bytes_written = self.serial_port.write(data)
            self.serial_port.flush()  # 确保数据发送完成
            
            self.logger.debug(f"指令已发送 ({bytes_written}字节): {command}")
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
        if not self.is_connected or not self.serial_port or not self.serial_port.is_open:
            self.logger.error("串口未打开，无法接收数据")
            return None
        
        try:
            # 临时设置超时时间
            original_timeout = self.serial_port.timeout
            self.serial_port.timeout = timeout
            
            # 读取一行数据（以换行符结束）
            line = self.serial_port.readline()
            
            # 恢复原始超时设置
            self.serial_port.timeout = original_timeout
            
            if not line:
                self.logger.debug("接收数据超时或无数据")
                return None
            
            # 解析JSON数据
            result = json.loads(line.decode('utf-8').strip())
            self.logger.debug(f"接收到数据: {result}")
            return result
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON解析失败: {e}, 原始数据: {line}")
            return None
        except Exception as e:
            self.logger.error(f"接收数据失败: {e}")
            return None
    
    def send_raw_bytes(self, data: bytes) -> bool:
        """
        发送原始字节数据
        
        Args:
            data: 要发送的字节数据
            
        Returns:
            bool: 发送成功返回True
        """
        if not self.is_connected or not self.serial_port or not self.serial_port.is_open:
            self.logger.error("串口未打开，无法发送数据")
            return False
        
        try:
            bytes_written = self.serial_port.write(data)
            self.serial_port.flush()
            self.logger.debug(f"原始数据已发送 ({bytes_written}字节)")
            return True
        except Exception as e:
            self.logger.error(f"发送原始数据失败: {e}")
            return False
    
    def receive_raw_bytes(self, size: int = 1, timeout: float = 1.0) -> Optional[bytes]:
        """
        接收原始字节数据
        
        Args:
            size: 要读取的字节数
            timeout: 超时时间（秒）
            
        Returns:
            Optional[bytes]: 接收到的字节数据
        """
        if not self.is_connected or not self.serial_port or not self.serial_port.is_open:
            self.logger.error("串口未打开，无法接收数据")
            return None
        
        try:
            original_timeout = self.serial_port.timeout
            self.serial_port.timeout = timeout
            
            data = self.serial_port.read(size)
            
            self.serial_port.timeout = original_timeout
            
            if not data:
                self.logger.debug("接收数据超时或无数据")
                return None
            
            self.logger.debug(f"接收到原始数据 ({len(data)}字节)")
            return data
            
        except Exception as e:
            self.logger.error(f"接收原始数据失败: {e}")
            return None
    
    def clear_buffers(self):
        """清空串口输入输出缓冲区"""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.reset_input_buffer()
            self.serial_port.reset_output_buffer()
            self.logger.debug("串口缓冲区已清空")
    
    @staticmethod
    def list_available_ports() -> List[str]:
        """
        列出系统中所有可用的串口
        
        Returns:
            List[str]: 可用串口列表
        """
        try:
            import serial.tools.list_ports
            ports = [port.device for port in serial.tools.list_ports.comports()]
            return ports
        except Exception as e:
            logging.error(f"列出串口失败: {e}")
            return []
