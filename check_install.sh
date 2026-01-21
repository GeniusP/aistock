#!/bin/bash
# 检查安装状态并提供下一步操作

echo "=========================================="
echo "量化交易系统 - 安装状态检查"
echo "=========================================="

# 检查虚拟环境
if [ -d "venv" ]; then
    echo "✅ 虚拟环境已创建"

    # 检查已安装的包
    echo ""
    echo "已安装的包:"
    source venv/bin/activate

    packages=("pandas" "numpy" "yfinance" "matplotlib" "seaborn" "scipy" "scikit-learn")

    for pkg in "${packages[@]}"; do
        if pip show "$pkg" &> /dev/null; then
            version=$(pip show "$pkg" | grep Version | cut -d' ' -f2)
            echo "  ✓ $pkg ($version)"
        else
            echo "  ✗ $pkg (未安装)"
        fi
    done

    echo ""
    echo "=========================================="
    echo "下一步操作"
    echo "=========================================="
    echo ""
    echo "1. 激活虚拟环境:"
    echo "   source venv/bin/activate"
    echo ""
    echo "2. 测试系统:"
    echo "   python test_system.py"
    echo ""
    echo "3. 运行演示:"
    echo "   python simple_demo.py"
    echo ""
    echo "4. 开始回测:"
    echo "   python main.py --symbol AAPL"
    echo ""

    # 检查pip是否还在运行
    if ps aux | grep -v grep | grep "pip install" > /dev/null; then
        echo "⏳ 依赖包安装仍在进行中..."
        echo "   请等待几分钟后再次运行此脚本"
    else
        echo "✅ 安装完成!"
    fi

else
    echo "❌ 虚拟环境未创建"
    echo ""
    echo "请先运行: ./setup.sh"
fi

echo ""
echo "=========================================="
