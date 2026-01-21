"""
离线模式的主程序
当无法连接Yahoo Finance时使用
"""

import pandas as pd
import numpy as np
import argparse
from datetime import datetime
import logging

from trading_strategies import (
    MovingAverageCrossover,
    MeanReversion,
    MomentumStrategy,
    RSIStrategy,
    MACDStrategy,
    BollingerBandsStrategy,
)
from backtest_engine import BacktestEngine
from performance_analytics import PerformanceAnalyzer, save_results_to_csv, create_html_report

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_mock_data(symbol="MOCK", period="2y"):
    """生成模拟股票数据"""
    np.random.seed(hash(symbol) % 10000)

    # 根据period确定天数
    period_days = {
        '1mo': 30,
        '3mo': 90,
        '6mo': 180,
        '1y': 365,
        '2y': 730,
    }

    n = period_days.get(period, 730)
    dates = pd.date_range(end=datetime.now(), periods=n, freq='D')

    # 模拟价格走势
    returns = np.random.normal(0.0005, 0.02, n)
    price = 100 * np.cumprod(1 + returns)

    data = pd.DataFrame({
        'datetime': dates,
        'open': price * (1 + np.random.uniform(-0.01, 0.01, n)),
        'high': price * (1 + np.random.uniform(0, 0.02, n)),
        'low': price * (1 + np.random.uniform(-0.02, 0, n)),
        'close': price,
        'volume': np.random.randint(1000000, 10000000, n)
    })

    logger.info(f"生成了 {len(data)} 条模拟数据 ({symbol})")
    return data


def create_strategy_from_name(name: str, params: dict = None):
    """根据策略名称创建策略对象"""
    params = params or {}

    strategies = {
        'moving_average_crossover': MovingAverageCrossover(
            short_window=params.get('short_window', 20),
            long_window=params.get('long_window', 50)
        ),
        'mean_reversion': MeanReversion(
            window=params.get('window', 20),
            entry_threshold=params.get('entry_threshold', 2.0),
            exit_threshold=params.get('exit_threshold', 0.5)
        ),
        'momentum': MomentumStrategy(
            lookback=params.get('lookback', 20),
            threshold=params.get('threshold', 0.02)
        ),
        'rsi': RSIStrategy(
            rsi_period=params.get('rsi_period', 14),
            oversold=params.get('oversold', 30),
            overbought=params.get('overbought', 70)
        ),
        'macd': MACDStrategy(
            fast=params.get('fast', 12),
            slow=params.get('slow', 26),
            signal=params.get('signal', 9)
        ),
        'bollinger_bands': BollingerBandsStrategy(
            window=params.get('window', 20),
            num_std=params.get('num_std', 2.0)
        )
    }

    if name not in strategies:
        raise ValueError(f"未知策略: {name}")

    return strategies[name]


def run_backtest(symbol: str, strategy_name: str = "moving_average_crossover"):
    """运行回测"""

    print("\n" + "=" * 80)
    print("量化交易回测系统 - 离线模式")
    print("=" * 80)
    print(f"\n⚠️  注意: 使用模拟数据进行演示")
    print(f"    实际使用时请确保网络连接正常\n")

    # 获取数据
    logger.info(f"步骤 1/3: 生成模拟数据")
    data = generate_mock_data(symbol, period="2y")

    # 创建策略
    logger.info(f"步骤 2/3: 创建策略")
    strategy = create_strategy_from_name(strategy_name)
    print(f"策略: {strategy.name}")

    # 运行回测
    logger.info(f"步骤 3/3: 执行回测")
    engine = BacktestEngine(
        strategy=strategy,
        initial_capital=100000,
        commission=0.001
    )
    results = engine.run(data, symbol)

    # 生成报告
    analyzer = PerformanceAnalyzer()
    report = analyzer.generate_report(results)
    print("\n" + report)

    # 保存结果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_results_to_csv(results, f"results/{symbol}_{strategy_name}_{timestamp}.csv")
    create_html_report(results, f"results/{symbol}_{strategy_name}_{timestamp}.html")

    # 绘制图表
    try:
        analyzer.plot_equity_curve(
            results['equity_curve'],
            save_path=f"results/{symbol}_{strategy_name}_equity_{timestamp}.png"
        )
        analyzer.plot_trade_analysis(
            results['trades'],
            save_path=f"results/{symbol}_{strategy_name}_trades_{timestamp}.png"
        )
    except Exception as e:
        logger.warning(f"绘制图表时出错: {str(e)}")

    return results


def run_multi_strategy_comparison(symbol: str = "MOCK"):
    """运行多策略对比"""

    print("\n" + "=" * 80)
    print("多策略对比分析 - 离线模式")
    print("=" * 80)

    # 获取数据
    data = generate_mock_data(symbol, period="2y")

    # 定义策略
    strategies = [
        ("MA交叉(20/50)", MovingAverageCrossover(20, 50)),
        ("MA交叉(10/30)", MovingAverageCrossover(10, 30)),
        ("MACD(12,26,9)", MACDStrategy(12, 26, 9)),
        ("RSI(14,30,70)", RSIStrategy(14, 30, 70)),
        ("布林带", BollingerBandsStrategy(20, 2.0)),
    ]

    results_comparison = []

    for name, strategy in strategies:
        print(f"\n回测策略: {name}")
        engine = BacktestEngine(strategy, initial_capital=100000)
        results = engine.run(data, symbol)

        results_comparison.append({
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

    df = pd.DataFrame(results_comparison)
    print(df.to_string(index=False))


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='量化交易回测系统 (离线模式)')
    parser.add_argument('--symbol', type=str, default='MOCK', help='交易标的 (离线模式使用模拟数据)')
    parser.add_argument('--strategy', type=str, default='moving_average_crossover',
                       choices=['moving_average_crossover', 'mean_reversion', 'momentum',
                               'rsi', 'macd', 'bollinger_bands'],
                       help='选择策略')
    parser.add_argument('--compare', action='store_true', help='运行多策略对比')

    args = parser.parse_args()

    if args.compare:
        run_multi_strategy_comparison(args.symbol)
    else:
        run_backtest(args.symbol, args.strategy)


if __name__ == "__main__":
    main()
