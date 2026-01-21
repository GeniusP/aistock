#!/usr/bin/env python3
"""
系统结构展示 - 不需要任何外部依赖
"""

import os
import sys

def show_project_structure():
    """展示项目结构"""
    print("=" * 80)
    print("量化交易系统 - 项目结构")
    print("=" * 80)

    print("\n📁 核心模块:")
    modules = [
        ("data_fetcher.py", "数据获取 - 支持Yahoo Finance", "4.0K"),
        ("technical_indicators.py", "技术指标 - 15+个常用指标", "7.9K"),
        ("trading_strategies.py", "交易策略 - 7种内置策略", "13K"),
        ("backtest_engine.py", "回测引擎 - 完整交易模拟", "12K"),
        ("risk_management.py", "风险管理 - 仓位控制和风险指标", "14K"),
        ("performance_analytics.py", "性能分析 - 可视化和报告", "17K"),
        ("main.py", "主程序 - 命令行工具", "9.1K"),
    ]

    for file, desc, size in modules:
        if os.path.exists(file):
            print(f"  ✓ {file:25s} {desc:40s} [{size}]")
        else:
            print(f"  ✗ {file:25s} {desc:40s} [缺失]")

    print("\n📚 文档:")
    docs = [
        ("START_HERE.md", "从这里开始! ⭐"),
        ("INSTALL_MAC.md", "Mac安装说明"),
        ("QUICKSTART.md", "快速开始指南"),
        ("README.md", "完整功能文档"),
        ("PROJECT_SUMMARY.md", "项目总结"),
    ]

    for file, desc in docs:
        if os.path.exists(file):
            print(f"  ✓ {file:25s} {desc}")
        else:
            print(f"  ✗ {file:25s} {desc}")

    print("\n🛠️ 工具脚本:")
    tools = [
        ("setup.sh", "一键安装脚本"),
        ("test_system.py", "系统测试脚本"),
        ("example.py", "示例代码"),
        ("simple_demo.py", "简化演示"),
    ]

    for file, desc in tools:
        if os.path.exists(file):
            print(f"  ✓ {file:25s} {desc}")
        else:
            print(f"  ✗ {file:25s} {desc}")

    print("\n⚙️ 配置文件:")
    configs = [
        ("config.yaml", "系统配置文件"),
        ("requirements.txt", "Python依赖列表"),
        (".gitignore", "Git忽略配置"),
    ]

    for file, desc in configs:
        if os.path.exists(file):
            print(f"  ✓ {file:25s} {desc}")
        else:
            print(f"  ✗ {file:25s} {desc}")


def show_strategies():
    """展示可用策略"""
    print("\n" + "=" * 80)
    print("内置交易策略")
    print("=" * 80)

    strategies = [
        {
            "name": "Moving Average Crossover",
            "desc": "移动平均线交叉策略",
            "params": "short_window=20, long_window=50",
            "logic": "短期均线上穿长期均线买入,下穿卖出"
        },
        {
            "name": "Mean Reversion",
            "desc": "均值回归策略",
            "params": "window=20, entry_threshold=2.0",
            "logic": "价格偏离均值过大时反向交易"
        },
        {
            "name": "Momentum Strategy",
            "desc": "动量策略",
            "params": "lookback=20, threshold=0.02",
            "logic": "价格动量向上买入,向下卖出"
        },
        {
            "name": "RSI Strategy",
            "desc": "RSI相对强弱指标策略",
            "params": "rsi_period=14, oversold=30, overbought=70",
            "logic": "RSI超卖买入,超买卖出"
        },
        {
            "name": "MACD Strategy",
            "desc": "MACD指标策略",
            "params": "fast=12, slow=26, signal=9",
            "logic": "MACD金叉买入,死叉卖出"
        },
        {
            "name": "Bollinger Bands",
            "desc": "布林带策略",
            "params": "window=20, num_std=2.0",
            "logic": "价格触及下轨买入,上轨卖出"
        },
        {
            "name": "Multi-Indicator",
            "desc": "多指标组合策略",
            "params": "consensus_threshold=0.6",
            "logic": "多个策略达成共识时交易"
        },
    ]

    for i, strategy in enumerate(strategies, 1):
        print(f"\n{i}. {strategy['name']}")
        print(f"   描述: {strategy['desc']}")
        print(f"   参数: {strategy['params']}")
        print(f"   逻辑: {strategy['logic']}")


def show_indicators():
    """展示技术指标"""
    print("\n" + "=" * 80)
    print("技术指标库")
    print("=" * 80)

    indicators = {
        "趋势指标": ["SMA - 简单移动平均", "EMA - 指数移动平均"],
        "动量指标": ["RSI - 相对强弱指标", "MACD - 指数平滑异同移动平均线",
                    "Stochastic - 随机指标", "Williams %R - 威廉指标"],
        "波动指标": ["Bollinger Bands - 布林带", "ATR - 平均真实波幅"],
        "成交量指标": ["OBV - 能量潮"],
        "其他指标": ["CCI - 商品通道指标"]
    }

    for category, items in indicators.items():
        print(f"\n{category}:")
        for item in items:
            print(f"  • {item}")


def show_risk_metrics():
    """展示风险指标"""
    print("\n" + "=" * 80)
    print("风险管理功能")
    print("=" * 80)

    print("\n仓位管理方法:")
    position_sizing = [
        "Fixed Ratio - 固定比例法",
        "Kelly Criterion - 凯利公式法",
        "ATR-Based - 基于ATR的方法",
        "Volatility Target - 波动率目标法"
    ]
    for method in position_sizing:
        print(f"  • {method}")

    print("\n风险指标:")
    risk_metrics = [
        "VaR (Value at Risk) - 风险价值",
        "CVaR (Conditional VaR) - 条件风险价值",
        "Maximum Drawdown - 最大回撤",
        "Sharpe Ratio - 夏普比率",
        "Sortino Ratio - 索提诺比率",
        "Calmar Ratio - 卡玛比率",
        "Information Ratio - 信息比率"
    ]
    for metric in risk_metrics:
        print(f"  • {metric}")


def show_usage_examples():
    """展示使用示例"""
    print("\n" + "=" * 80)
    print("使用示例")
    print("=" * 80)

    print("\n1. 命令行方式:")
    print("   python main.py --symbol AAPL")
    print("   python main.py --symbols AAPL MSFT GOOGL")
    print("   python main.py --symbol AAPL --strategy macd")
    print("   python main.py --compare --symbol AAPL")

    print("\n2. Python代码:")
    print("""
   from data_fetcher import DataFetcher
   from trading_strategies import MovingAverageCrossover
   from backtest_engine import BacktestEngine

   # 获取数据
   fetcher = DataFetcher()
   data = fetcher.fetch_data("AAPL", period="2y")

   # 创建策略
   strategy = MovingAverageCrossover(20, 50)

   # 运行回测
   engine = BacktestEngine(strategy, initial_capital=100000)
   results = engine.run(data, "AAPL")

   # 查看结果
   print(f"收益率: {results['total_return']:.2%}")
    """)


def show_next_steps():
    """展示下一步操作"""
    print("\n" + "=" * 80)
    print("下一步操作")
    print("=" * 80)

    print("\n1️⃣  安装依赖:")
    print("   ./setup.sh")
    print("   或:")
    print("   python3 -m venv venv")
    print("   source venv/bin/activate")
    print("   pip install pandas numpy yfinance matplotlib seaborn")

    print("\n2️⃣  测试系统:")
    print("   python test_system.py")

    print("\n3️⃣  运行演示:")
    print("   python simple_demo.py")

    print("\n4️⃣  开始回测:")
    print("   python main.py --symbol AAPL")

    print("\n5️⃣  查看文档:")
    print("   cat START_HERE.md")
    print("   open START_HERE.md  # 在浏览器中打开")


def main():
    """主函数"""
    try:
        show_project_structure()
        show_strategies()
        show_indicators()
        show_risk_metrics()
        show_usage_examples()
        show_next_steps()

        print("\n" + "=" * 80)
        print("🎉 系统已就绪!")
        print("=" * 80)
        print(f"\n📁 当前目录: {os.getcwd()}")
        print(f"📊 总文件数: {len([f for f in os.listdir('.') if os.path.isfile(f)])}")
        print("\n💡 现在运行 ./setup.sh 开始安装!")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
