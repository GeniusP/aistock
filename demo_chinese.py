#!/usr/bin/env python3
"""
中文版快速演示
使用Alpha Vantage真实数据
"""

import sys
sys.path.insert(0, '/Users/user/Desktop/量化ai')

import pandas as pd
from datetime import datetime

print("""
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║           📊 量化交易回测系统 - 中文演示版                          ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
""")

# 导入模块
from data_fetcher import DataFetcher
from trading_strategies import MovingAverageCrossover
from backtest_engine import BacktestEngine
from chinese_analytics import ChinesePerformanceAnalyzer

print("📡 正在获取AAPL股票数据... (Alpha Vantage API)")

fetcher = DataFetcher(source="alpha_vantage", api_key="RQMP1U6N9J2OMIWH")
data = fetcher.fetch_data("AAPL", period="6mo")

if not data.empty:
    print(f"✅ 成功获取 {len(data)} 条真实数据")
    print(f"   时间范围: {data['datetime'].iloc[0]} 至 {data['datetime'].iloc[-1]}")
else:
    print("❌ 数据获取失败")
    sys.exit(1)

print("\n🎯 策略: 移动平均线交叉 (MA 20/50)")
print("⚙️ 正在执行回测...")

strategy = MovingAverageCrossover(short_window=20, long_window=50)
engine = BacktestEngine(strategy, initial_capital=100000, commission=0.001)
results = engine.run(data, "AAPL")

print("\n" + "="*80)
print("回测报告")
print("="*80)

analyzer = ChinesePerformanceAnalyzer()

# 基础报告
report = analyzer.generate_chinese_report(results)
print(report)

# 计算高级指标
equity_curve = results['equity_curve']
advanced = analyzer.calculate_advanced_metrics(equity_curve)

print("【高级量化指标】")
print(f"年化收益率: {advanced['annual_return']:.2%}")
print(f"波动率: {advanced['volatility']:.2%}")
print(f"索提诺比率: {advanced['sortino_ratio']:.2f}")
print(f"卡玛比率: {advanced['calmar_ratio']:.2f}")
print(f"VaR (95%): {advanced['var_95']:.2%}")

print("\n" + "="*80)
print("✅ 回测完成!")
print("="*80)

print("\n💡 特点:")
print("  ✓ 使用Alpha Vantage真实数据")
print("  ✓ 中文界面和报告")
print("  ✓ 高级量化指标")
print("  ✓ 专业可视化")

print("\n📊 查看更多:")
print("  python main_chinese.py --symbol AAPL --strategy ma")
print("  python main_chinese.py --symbol MSFT --strategy macd")
