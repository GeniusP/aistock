#!/usr/bin/env python3
"""
简化演示脚本 - 不需要额外依赖,直接演示系统功能
"""

import sys
import os

print("=" * 80)
print("量化交易系统 - 功能演示")
print("=" * 80)

# 检查必要的模块
print("\n检查依赖...")
missing_modules = []

try:
    import pandas as pd
    print("✓ pandas")
except ImportError:
    missing_modules.append("pandas")

try:
    import numpy as np
    print("✓ numpy")
except ImportError:
    missing_modules.append("numpy")

try:
    import yfinance as yf
    print("✓ yfinance")
except ImportError:
    missing_modules.append("yfinance")

if missing_modules:
    print(f"\n❌ 缺少依赖: {', '.join(missing_modules)}")
    print("\n请先运行: ./setup.sh")
    print("或手动安装:")
    print(f"  pip install {' '.join(missing_modules)}")
    sys.exit(1)

print("\n✅ 所有依赖已安装!")

# 现在运行演示
print("\n" + "=" * 80)
print("开始演示...")
print("=" * 80)

try:
    from data_fetcher import DataFetcher
    from trading_strategies import MovingAverageCrossover
    from backtest_engine import BacktestEngine

    # 步骤1: 获取数据
    print("\n步骤 1/3: 获取股票数据...")
    fetcher = DataFetcher()
    data = fetcher.fetch_data("AAPL", period="6mo")

    if data.empty:
        print("❌ 无法获取数据,请检查网络连接")
        sys.exit(1)

    print(f"✓ 成功获取 {len(data)} 条数据")
    print(f"  日期范围: {data['datetime'].iloc[0]} 到 {data['datetime'].iloc[-1]}")
    print(f"  价格范围: ${data['close'].min():.2f} - ${data['close'].max():.2f}")

    # 步骤2: 创建策略
    print("\n步骤 2/3: 创建交易策略...")
    strategy = MovingAverageCrossover(short_window=20, long_window=50)
    print(f"✓ 策略: {strategy.name}")
    print(f"  参数: 短期均线={strategy.short_window}, 长期均线={strategy.long_window}")

    # 步骤3: 运行回测
    print("\n步骤 3/3: 执行回测...")
    engine = BacktestEngine(
        strategy=strategy,
        initial_capital=100000,
        commission=0.001
    )
    results = engine.run(data, "AAPL")

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

    print(f"\n📌 基准对比:")
    print(f"  策略收益: {results['total_return']:.2%}")
    print(f"  买入持有: {results['buy_hold_return']:.2%}")
    print(f"  超额收益: {results['total_return'] - results['buy_hold_return']:.2%}")

    # 显示最近几笔交易
    if results['trades']:
        print(f"\n📝 最近3笔交易:")
        for i, trade in enumerate(results['trades'][-3:], 1):
            if trade.pnl is not None:
                profit_str = "✓ 盈利" if trade.pnl > 0 else "✗ 亏损"
                print(f"  {i}. {trade.entry_date.strftime('%Y-%m-%d')} → {trade.exit_date.strftime('%Y-%m-%d')}")
                print(f"     入场: ${trade.entry_price:.2f} | 出场: ${trade.exit_price:.2f}")
                print(f"     收益: ${trade.pnl:.2f} ({trade.pnl_pct:.2%}) {profit_str}")

    print("\n" + "=" * 80)
    print("✅ 回测完成!")
    print("=" * 80)

    print("\n💡 下一步:")
    print("  • 查看完整文档: README.md")
    print("  • 尝试其他策略: python main.py --symbol AAPL --strategy macd")
    print("  • 对比多个策略: python main.py --compare --symbol AAPL")
    print("  • 修改配置文件: config.yaml")

except Exception as e:
    print(f"\n❌ 错误: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
