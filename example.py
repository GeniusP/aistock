"""
示例脚本: 快速开始量化交易回测
"""

from data_fetcher import DataFetcher
from technical_indicators import TechnicalIndicators
from trading_strategies import MovingAverageCrossover, MACDStrategy
from backtest_engine import BacktestEngine
from performance_analytics import PerformanceAnalyzer


def quick_start_example():
    """快速开始示例"""
    print("=" * 80)
    print("量化交易系统 - 快速开始示例")
    print("=" * 80)

    # 步骤1: 获取数据
    print("\n步骤1: 获取AAPL股票数据...")
    fetcher = DataFetcher()
    data = fetcher.fetch_data("AAPL", period="1y")
    print(f"获取了 {len(data)} 条数据")

    # 步骤2: 添加技术指标
    print("\n步骤2: 计算技术指标...")
    data_with_indicators = TechnicalIndicators.add_all_indicators(data)
    print(f"添加了 {len(data_with_indicators.columns) - len(data.columns)} 个技术指标")

    # 步骤3: 创建并运行策略
    print("\n步骤3: 运行MA交叉策略...")
    strategy = MovingAverageCrossover(short_window=20, long_window=50)
    engine = BacktestEngine(strategy, initial_capital=100000, commission=0.001)
    results = engine.run(data, "AAPL")

    # 步骤4: 查看结果
    print("\n步骤4: 回测结果")
    analyzer = PerformanceAnalyzer()
    report = analyzer.generate_report(results)
    print(report)

    return results


def multi_strategy_comparison():
    """多策略对比示例"""
    print("\n" + "=" * 80)
    print("多策略对比示例")
    print("=" * 80)

    # 获取数据
    fetcher = DataFetcher()
    data = fetcher.fetch_data("MSFT", period="2y")

    # 定义多个策略
    strategies = [
        ("MA交叉(20/50)", MovingAverageCrossover(20, 50)),
        ("MA交叉(10/30)", MovingAverageCrossover(10, 30)),
        ("MACD(12,26,9)", MACDStrategy(12, 26, 9)),
    ]

    results_summary = []

    for name, strategy in strategies:
        print(f"\n回测策略: {name}")
        engine = BacktestEngine(strategy, initial_capital=100000)
        results = engine.run(data, "MSFT")

        results_summary.append({
            '策略': name,
            '收益率': f"{results['total_return']:.2%}",
            '夏普比率': f"{results['sharpe_ratio']:.2f}",
            '最大回撤': f"{results['max_drawdown']:.2%}",
            '胜率': f"{results['win_rate']:.2%}",
            '交易次数': results['total_trades']
        })

    # 打印对比表
    print("\n" + "=" * 80)
    print("策略对比结果")
    print("=" * 80)
    for result in results_summary:
        print(f"\n{result['策略']}:")
        for key, value in result.items():
            if key != '策略':
                print(f"  {key}: {value}")


def technical_indicators_demo():
    """技术指标演示"""
    print("\n" + "=" * 80)
    print("技术指标演示")
    print("=" * 80)

    # 获取数据
    fetcher = DataFetcher()
    data = fetcher.fetch_data("GOOGL", period="6mo")

    # 添加所有技术指标
    data_with_indicators = TechnicalIndicators.add_all_indicators(data)

    # 显示最新的指标值
    print("\n最新技术指标值:")
    latest = data_with_indicators.iloc[-1]

    indicators_to_show = [
        'close', 'sma_20', 'sma_50', 'rsi', 'macd',
        'bb_upper', 'bb_middle', 'bb_lower', 'atr'
    ]

    for indicator in indicators_to_show:
        if indicator in latest:
            print(f"{indicator:15s}: {latest[indicator]:.2f}")


if __name__ == "__main__":
    import pandas as pd

    # 运行快速开始示例
    results = quick_start_example()

    # 运行多策略对比
    multi_strategy_comparison()

    # 运行技术指标演示
    technical_indicators_demo()

    print("\n" + "=" * 80)
    print("示例运行完成!")
    print("=" * 80)
