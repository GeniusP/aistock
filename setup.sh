#!/bin/bash
# 快速安装脚本

echo "=========================================="
echo "量化交易系统 - 环境设置"
echo "=========================================="

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python3,请先安装Python"
    exit 1
fi

echo "✅ 找到Python: $(python3 --version)"

# 创建虚拟环境
echo ""
echo "📦 创建虚拟环境..."
python3 -m venv venv

# 激活虚拟环境
echo "🔌 激活虚拟环境..."
source venv/bin/activate

# 升级pip
echo ""
echo "⬆️  升级pip..."
pip install --upgrade pip -q

# 安装依赖
echo ""
echo "📥 安装依赖包..."
echo "这可能需要几分钟..."

pip install pandas numpy yfinance matplotlib seaborn scipy scikit-learn plotly backtrader -q

echo ""
echo "✅ 依赖安装完成!"
echo ""
echo "=========================================="
echo "下一步:"
echo "=========================================="
echo ""
echo "1. 激活虚拟环境:"
echo "   source venv/bin/activate"
echo ""
echo "2. 运行测试:"
echo "   python test_system.py"
echo ""
echo "3. 运行示例:"
echo "   python example.py"
echo ""
echo "4. 开始回测:"
echo "   python main.py --symbol AAPL"
echo ""
echo "祝您使用愉快! 📈"
echo "=========================================="
