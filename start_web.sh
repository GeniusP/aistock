#!/bin/bash
# 启动A股市场情绪分析Web服务器

echo """
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║              🌐 A股市场情绪分析Web面板                             ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
"""

# 进入项目目录
cd /Users/user/Desktop/量化ai

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在，请先创建虚拟环境"
    exit 1
fi

# 激活虚拟环境
echo "✅ 激活虚拟环境..."
source venv/bin/activate

# 检查Flask是否安装
python -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Flask未安装，正在安装..."
    pip install flask
fi

echo ""
echo "🚀 正在启动Web服务器..."
echo ""
echo "📊 访问地址:"
echo "   本地: http://localhost:5000"
echo "   局域网: http://$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo '你的IP'):5000"
echo ""
echo "💡 提示:"
echo "   • 按 Ctrl+C 停止服务器"
echo "   • 服务器启动后会自动打开浏览器"
echo ""
echo "="*80
echo ""

# 启动服务器
python web_server.py
