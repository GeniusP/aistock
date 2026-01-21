#!/usr/bin/env python3
"""
离线演示 - 使用模拟数据演示系统功能
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

print("=" * 80)
print("量化交易系统 - 离线演示")
print("=" * 80)

# 生成模拟数据
print("\n📊 生成模拟市场数据...")
np.random.seed(42)

# 生成2年的日线数据
dates = pd.date_range(start='2022-01-01', end='2024-01-01', freq='D')
n = len(dates)

# 模拟价格走势(随机游走)
returns = np.random.normal(0.0005, 0.02, n)
price = 100 * np.cumprod(1 + returns)

# 创建OHLCV数据
data = pd.DataFrame({
    'datetime': dates,
    'open': price * (1 + np.random.uniform(-0.01, 0.01, n)),
    'high': price * (1 + np.random.uniform(0, 0.02, n)),
    'low': price * (1 + np.random.uniform(-0.02, 0, n)),
    'close': price,
    'volume': np.random.randint(1000000, 10000000, n)
})

print(f"✓ 生成了 {len(data)} 条模拟数据")
print(f"  日期范围: {data['datetime'].iloc[0]} 到 {data['datetime'].iloc[-1]}")
print(f"  价格范围: ${data['close'].min():.2f} - ${data['close'].max():.2f}")

# 导入系统模块
from trading_strategies import MovingAverageCrossover
from backtest_engine import BacktestEngine

# 创建策略
print("\n🎯 创建交易策略...")
strategy = MovingAverageCrossover(short_window=20, long_window=50)
print(f"✓ 策略: {strategy.name}")
print(f"  参数: 短期均线={strategy.short_window}, 长期均线={strategy.long_window}")

# 运行回测
print("\n⚙️ 执行回测...")
engine = BacktestEngine(
    strategy=strategy,
    initial_capital=100000,
    commission=0.001
)
results = engine.run(data, "DEMO")

# 显示结果
print("\n" + "=" * 80)
print("回测结果")
print("=" * 80)

print(f"\n💰 资金:")
print(f"  初始资金: ${results['initial_capital']:,.2f}")
print(f"  最终资金: ${results['final_value']:,.2f}")
print(f"  总收益: ${results['final_value'] - results['initial_capital']:,.2f}")
print(f"  总收益率: {results['total_return']:.2%}")

print(f"\n📊 风险指标:")
print(f"  夏普比率: {results['sharpe_ratio']:.2f}")
print(f"  最大回撤: {results['max_drawdown']:.2%}")

print(f"\n📈 交易统计:")
print(f"  总交易次数: {results['total_trades']}")
print(f"  盈利交易: {results['winning_trades']}")
print(f"  亏损交易: {results['losing_trades']}")
print(f"  胜率: {results['win_rate']:.2%}")
print(f"  盈亏比: {results['profit_factor']:.2f}")

# 显示权益曲线摘要
equity_curve = results['equity_curve']
print(f"\n📈 权益曲线摘要:")
print(f"  最高权益: ${equity_curve['portfolio_value'].max():,.2f}")
print(f"  最低权益: ${equity_curve['portfolio_value'].min():,.2f}")
print(f"  平均权益: ${equity_curve['portfolio_value'].mean():,.2f}")

# 显示最近几笔交易
if results['trades']:
    print(f"\n📝 最近5笔交易:")
    for i, trade in enumerate(results['trades'][-5:], 1):
        if trade.exit_date and trade.pnl is not None:
            profit_str = "✓ 盈利" if trade.pnl > 0 else "✗ 亏损"
            print(f"  {i}. {trade.entry_date.strftime('%Y-%m-%d')} → {trade.exit_date.strftime('%Y-%m-%d')}")
            print(f"     入场: ${trade.entry_price:.2f} | 出场: ${trade.exit_price:.2f}")
            print(f"     收益: ${trade.pnl:.2f} ({trade.pnl_pct:.2%}) {profit_str}")

print("\n" + "=" * 80)
print("✅ 离线演示完成!")
print("=" * 80)

print("\n💡 说明:")
print("  • 本演示使用随机生成的模拟数据")
print("  • 实际使用时,系统会从Yahoo Finance获取真实数据")
print("  • 如遇API限流,请稍后重试或使用VPN")

print("\n📚 下一步:")
print("  • 在线测试: python test_system.py")
print("  • 查看文档: cat START_HERE.md")
print("  • 真实回测: python main.py --symbol AAPL")
print("  • 尝试其他策略: python main.py --compare --symbol AAPL")

print("\n" + "=" * 80)
