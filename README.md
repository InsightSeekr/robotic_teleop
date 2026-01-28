# robotic_teleop
机器人遥操作系统

## 项目简介

这是一个灵活的机器人遥操作接口库，支持多种通信方式（Socket和串口），可用于机器人远程控制和数据交互。

## 功能特性

- **多种通信方式**：
  - Socket通信（支持TCP和UDP协议）
  - 串口通信（支持RS232、RS485等）
- **统一接口设计**：基于抽象基类的一致API
- **完整的客户端/服务器支持**：Socket支持双向通信
- **原始数据支持**：支持JSON和原始字节数据传输
- **灵活配置**：可自定义端口、波特率、超时等参数
- **详细日志**：内置日志记录，便于调试

## 目录结构

```
robotic_teleop/
├── README.md                  # 项目文档
├── requirements.txt           # 依赖包列表
├── teleop_interface.py        # 遥操作接口基类
├── socket_teleop.py           # Socket通信实现
├── serial_teleop.py           # 串口通信实现
└── examples.py                # 使用示例
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 快速开始

### 1. Socket TCP通信示例

**客户端代码：**

```python
from socket_teleop import SocketTeleopInterface
import time

# 创建TCP客户端
client = SocketTeleopInterface(
    host="127.0.0.1",
    port=8888,
    protocol="TCP"
)

# 连接到服务器
if client.connect():
    # 发送控制指令
    command = {
        "type": "move",
        "linear_velocity": 0.5,
        "angular_velocity": 0.3,
        "timestamp": time.time()
    }
    client.send_command(command)
    
    # 接收反馈
    feedback = client.receive_data(timeout=2.0)
    print(f"反馈: {feedback}")
    
    # 断开连接
    client.disconnect()
```

**服务器端代码：**

```python
from socket_teleop import SocketTeleopServer
import time

# 创建TCP服务器
server = SocketTeleopServer(
    host="0.0.0.0",
    port=8888,
    protocol="TCP"
)

# 启动服务器
if server.connect():
    # 接收客户端指令
    command = server.receive_data(timeout=5.0)
    print(f"接收到指令: {command}")
    
    # 发送反馈
    feedback = {
        "status": "success",
        "position": [1.2, 3.4, 5.6],
        "timestamp": time.time()
    }
    server.send_command(feedback)
    
    # 关闭服务器
    server.disconnect()
```

### 2. Socket UDP通信示例

```python
from socket_teleop import SocketTeleopInterface

# 创建UDP客户端
client = SocketTeleopInterface(
    host="127.0.0.1",
    port=9999,
    protocol="UDP"
)

if client.connect():
    command = {"type": "status_query"}
    client.send_command(command)
    client.disconnect()
```

### 3. 串口通信示例

```python
from serial_teleop import SerialTeleopInterface
import time

# 列出可用串口
ports = SerialTeleopInterface.list_available_ports()
print(f"可用串口: {ports}")

# 创建串口接口
serial = SerialTeleopInterface(
    port="/dev/ttyUSB0",  # Linux: /dev/ttyUSB0, Windows: COM3
    baudrate=115200,
    timeout=1.0
)

if serial.connect():
    # 发送JSON指令
    command = {
        "type": "move",
        "speed": 100,
        "direction": "forward"
    }
    serial.send_command(command)
    
    # 接收反馈
    feedback = serial.receive_data(timeout=2.0)
    print(f"反馈: {feedback}")
    
    # 发送原始字节数据
    serial.send_raw_bytes(b'\x01\x02\x03')
    
    # 接收原始字节数据
    raw_data = serial.receive_raw_bytes(size=5, timeout=1.0)
    
    serial.disconnect()
```

## API文档

### TeleopInterface（基类）

所有遥操作接口的抽象基类，定义了标准接口：

- `connect() -> bool`: 建立连接
- `disconnect() -> bool`: 断开连接
- `send_command(command: Dict) -> bool`: 发送控制指令
- `receive_data(timeout: float) -> Optional[Dict]`: 接收数据
- `check_connection() -> bool`: 检查连接状态

### SocketTeleopInterface（Socket客户端）

**初始化参数：**
- `host`: 服务器地址（默认：127.0.0.1）
- `port`: 端口号（默认：8888）
- `protocol`: 协议类型，"TCP"或"UDP"（默认：TCP）
- `buffer_size`: 缓冲区大小（默认：4096）

**特点：**
- 支持TCP和UDP两种协议
- JSON格式数据传输
- 自动重连机制

### SocketTeleopServer（Socket服务器）

**初始化参数：**
- `host`: 监听地址（默认：0.0.0.0）
- `port`: 端口号（默认：8888）
- `protocol`: 协议类型，"TCP"或"UDP"（默认：TCP）
- `buffer_size`: 缓冲区大小（默认：4096）

**特点：**
- 支持TCP和UDP服务器
- 等待客户端连接
- 双向数据传输

### SerialTeleopInterface（串口接口）

**初始化参数：**
- `port`: 串口设备路径（默认：/dev/ttyUSB0）
- `baudrate`: 波特率（默认：115200）
- `timeout`: 读取超时时间（默认：1.0秒）
- `bytesize`: 数据位（默认：8）
- `parity`: 校验位（默认：'N'无校验）
- `stopbits`: 停止位（默认：1）

**特点：**
- 支持JSON和原始字节数据
- 自动缓冲区管理
- 静态方法列出可用串口

**额外方法：**
- `send_raw_bytes(data: bytes) -> bool`: 发送原始字节
- `receive_raw_bytes(size: int, timeout: float) -> Optional[bytes]`: 接收原始字节
- `clear_buffers()`: 清空缓冲区
- `list_available_ports() -> List[str]`: 列出可用串口（静态方法）

## 运行示例程序

```bash
python examples.py
```

示例程序提供交互式菜单，可以测试各种通信方式。

## 常见问题

### 1. 串口权限问题（Linux）

如果遇到串口权限错误，可以：

```bash
# 方法1：将用户添加到dialout组
sudo usermod -a -G dialout $USER
# 注销后重新登录生效

# 方法2：临时授予权限
sudo chmod 666 /dev/ttyUSB0
```

### 2. 找不到串口设备

```python
# 使用工具查看可用串口
from serial_teleop import SerialTeleopInterface
ports = SerialTeleopInterface.list_available_ports()
print(ports)
```

### 3. Socket连接失败

- 检查防火墙设置
- 确认IP地址和端口号正确
- 确保服务器端已启动（TCP模式）

## 开发计划

- [ ] 添加WebSocket支持
- [ ] 实现数据加密
- [ ] 添加心跳检测机制
- [ ] 支持多客户端连接
- [ ] 添加数据压缩选项

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！
