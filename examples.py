"""
机器人遥操作接口使用示例
演示Socket和串口两种接口的使用方法
"""
from socket_teleop import SocketTeleopInterface, SocketTeleopServer
from serial_teleop import SerialTeleopInterface
import time


def socket_client_example():
    """Socket客户端示例 - TCP协议"""
    print("=" * 50)
    print("Socket客户端示例 (TCP)")
    print("=" * 50)
    
    # 创建Socket客户端（TCP）
    client = SocketTeleopInterface(
        host="127.0.0.1",
        port=8888,
        protocol="TCP"
    )
    
    # 连接到服务器
    if not client.connect():
        print("连接失败！")
        return
    
    try:
        # 发送控制指令
        command = {
            "type": "move",
            "linear_velocity": 0.5,
            "angular_velocity": 0.3,
            "timestamp": time.time()
        }
        print(f"\n发送指令: {command}")
        client.send_command(command)
        
        # 接收反馈数据
        print("\n等待接收反馈...")
        feedback = client.receive_data(timeout=2.0)
        if feedback:
            print(f"接收到反馈: {feedback}")
        else:
            print("未收到反馈数据")
            
    finally:
        # 断开连接
        client.disconnect()
        print("\n客户端已断开连接")


def socket_server_example():
    """Socket服务器端示例 - TCP协议"""
    print("=" * 50)
    print("Socket服务器端示例 (TCP)")
    print("=" * 50)
    
    # 创建Socket服务器
    server = SocketTeleopServer(
        host="0.0.0.0",
        port=8888,
        protocol="TCP"
    )
    
    # 启动服务器并等待客户端连接
    print("\n等待客户端连接...")
    if not server.connect():
        print("服务器启动失败！")
        return
    
    try:
        # 接收客户端指令
        print("\n等待接收客户端指令...")
        command = server.receive_data(timeout=5.0)
        if command:
            print(f"接收到指令: {command}")
            
            # 发送反馈数据
            feedback = {
                "status": "success",
                "position": [1.2, 3.4, 5.6],
                "velocity": 0.5,
                "timestamp": time.time()
            }
            print(f"\n发送反馈: {feedback}")
            server.send_command(feedback)
        else:
            print("未收到客户端指令")
            
    finally:
        # 关闭服务器
        server.disconnect()
        print("\n服务器已关闭")


def socket_udp_example():
    """Socket客户端示例 - UDP协议"""
    print("=" * 50)
    print("Socket客户端示例 (UDP)")
    print("=" * 50)
    
    # 创建Socket客户端（UDP）
    client = SocketTeleopInterface(
        host="127.0.0.1",
        port=9999,
        protocol="UDP"
    )
    
    # 创建UDP socket
    if not client.connect():
        print("创建UDP socket失败！")
        return
    
    try:
        # 发送控制指令
        command = {
            "type": "stop",
            "emergency": False,
            "timestamp": time.time()
        }
        print(f"\n发送指令: {command}")
        client.send_command(command)
        
        # 接收反馈（UDP可能不会收到响应）
        print("\n等待接收反馈...")
        feedback = client.receive_data(timeout=1.0)
        if feedback:
            print(f"接收到反馈: {feedback}")
        else:
            print("UDP模式下未收到反馈（这是正常的）")
            
    finally:
        client.disconnect()
        print("\nUDP客户端已断开")


def serial_example():
    """串口通信示例"""
    print("=" * 50)
    print("串口通信示例")
    print("=" * 50)
    
    # 列出可用串口
    available_ports = SerialTeleopInterface.list_available_ports()
    print(f"\n可用串口: {available_ports}")
    
    # 创建串口接口
    # 注意：需要根据实际情况修改串口设备路径
    serial_interface = SerialTeleopInterface(
        port="/dev/ttyUSB0",  # Linux下的串口，Windows下使用"COM3"等
        baudrate=115200,
        timeout=1.0
    )
    
    # 尝试打开串口
    print(f"\n尝试打开串口: {serial_interface.port}")
    if not serial_interface.connect():
        print("串口打开失败！请检查：")
        print("1. 串口设备是否连接")
        print("2. 串口路径是否正确")
        print("3. 是否有访问权限 (Linux下可能需要 sudo 或添加用户到dialout组)")
        return
    
    try:
        # 清空缓冲区
        serial_interface.clear_buffers()
        
        # 发送控制指令
        command = {
            "type": "move",
            "speed": 100,
            "direction": "forward",
            "timestamp": time.time()
        }
        print(f"\n发送指令: {command}")
        serial_interface.send_command(command)
        
        # 等待一小段时间
        time.sleep(0.1)
        
        # 接收反馈数据
        print("\n等待接收反馈...")
        feedback = serial_interface.receive_data(timeout=2.0)
        if feedback:
            print(f"接收到反馈: {feedback}")
        else:
            print("未收到反馈数据")
        
        # 原始字节数据示例
        print("\n\n发送原始字节数据示例:")
        raw_data = b'\x01\x02\x03\x04\x05'
        print(f"发送原始数据: {raw_data.hex()}")
        serial_interface.send_raw_bytes(raw_data)
        
        # 接收原始字节数据
        print("\n接收原始字节数据...")
        raw_feedback = serial_interface.receive_raw_bytes(size=5, timeout=1.0)
        if raw_feedback:
            print(f"接收到原始数据: {raw_feedback.hex()}")
        else:
            print("未收到原始数据")
            
    finally:
        # 关闭串口
        serial_interface.disconnect()
        print("\n串口已关闭")


def main():
    """主函数 - 运行所有示例"""
    print("\n" + "=" * 50)
    print("机器人遥操作接口示例程序")
    print("=" * 50)
    
    while True:
        print("\n请选择要运行的示例:")
        print("1. Socket TCP客户端示例")
        print("2. Socket TCP服务器端示例")
        print("3. Socket UDP客户端示例")
        print("4. 串口通信示例")
        print("0. 退出")
        
        choice = input("\n请输入选项 (0-4): ").strip()
        
        if choice == "1":
            socket_client_example()
        elif choice == "2":
            socket_server_example()
        elif choice == "3":
            socket_udp_example()
        elif choice == "4":
            serial_example()
        elif choice == "0":
            print("\n再见！")
            break
        else:
            print("\n无效选项，请重新选择")
        
        input("\n按回车键继续...")


if __name__ == "__main__":
    main()
