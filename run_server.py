#!/usr/bin/env python3
"""
启动Web服务器的简化脚本
"""

import sys
sys.path.insert(0, '/Users/user/Desktop/量化ai')

import subprocess
import webbrowser
import time
import os

def main():
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║              🌐 A股市场情绪分析Web服务器                           ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
    """)

    print("🚀 正在启动Web服务器...")
    print("\n📊 服务器信息:")
    print("   地址: http://localhost:5000")
    print("   状态: 启动中...\n")

    # 激活虚拟环境并启动服务器
    cmd = "source venv/bin/activate && python web_server.py"

    print("💡 使用提示:")
    print("   1. 服务器启动后，按 Ctrl+C 停止")
    print("   2. 在浏览器中访问: http://localhost:5000")
    print("   3. 查看 API: http://localhost:5000/api/sentiment")
    print("\n" + "="*80 + "\n")

    # 启动服务器
    os.system("bash -c '" + cmd + "'")

if __name__ == "__main__":
    main()
