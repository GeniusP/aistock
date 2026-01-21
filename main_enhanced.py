"""
增强版主程序 - 支持多数据源,自动切换避免API限流
"""

import pandas as pd
import numpy as np
import argparse
from datetime import datetime
import logging
import sys

# 使用增强版数据获取器
from data_fetcher_enhanced import EnhancedDataFetcher

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

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


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


def run_backtest(symbol: str, strategy_name: str = "moving_average_crossover",
                sources: list = None, period: str = "2y"):
    """运行回测"""

    print("\n" + "=" * 80)
    print("量化交易回测系统 - 增强版")
    print("=" * 80)

    # 显示数据源
    sources = sources or ['yahoo', 'mock']
    print(f"\n📡 数据源 (按优先级): {', '.join(sources)}")

    # 获取数据
    logger.info(f"步骤 1/3: 获取数据")
    fetcher = EnhancedDataFetcher(sources=sources)

    print(f"正在获取 {symbol} 数据...")
    data = fetcher.fetch_data(symbol, period=period)

    if data.empty:
        print(f"\n❌ 无法获取 {symbol} 的数据")
        print("\n💡 建议:")
        print("  • 检查网络连接")
        print("  • 稍后重试")
        print("  • 使用 --sources mock 强制使用模拟数据")
        return None

    # 显示数据信息
    data_source = "真实数据" if len(data['close'].unique()) > 100 else "模拟数据"
    print(f"\n✓ 成功获取 {len(data)} 条数据 ({data_source})")
    print(f"  日期范围: {data['datetime'].iloc[0]} 到 {data['datetime'].iloc[-1]}")
    print(f"  价格范围: ${data['close'].min():.2f} - ${data['close'].max():.2f}")

    # 创建策略
    logger.info(f"步骤 2/3: 创建策略")
    strategy = create_strategy_from_name(strategy_name)
    print(f"\n策略: {strategy.name}")

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

    print(f"\n💾 结果已保存到 results/ 目录")

    # 绘制图表
    try:
        print("\n📊 正在生成图表...")
        analyzer.plot_equity_curve(
            results['equity_curve'],
            save_path=f"results/{symbol}_{strategy_name}_equity_{timestamp}.png"
        )
        analyzer.plot_trade_analysis(
            results['trades'],
            save_path=f"results/{symbol}_{strategy_name}_trades_{timestamp}.png"
        )
        print("✓ 图表生成完成")
    except Exception as e:
        logger.warning(f"绘制图表时出错: {str(e)}")

    return results


def run_multi_strategy_comparison(symbol: str = "AAPL", sources: list = None):
    """运行多策略对比"""

    print("\n" + "=" * 80)
    print("多策略对比分析 - 增强版")
    print("=" * 80)

    sources = sources or ['yahoo', 'mock']
    print(f"\n📡 数据源: {', '.join(sources)}")

    # 获取数据
    fetcher = EnhancedDataFetcher(sources=sources)
    print(f"\n正在获取 {symbol} 数据...")
    data = fetcher.fetch_data(symbol, period="2y")

    if data.empty:
        print(f"\n❌ 无法获取 {symbol} 的数据")
        return

    print(f"✓ 成功获取 {len(data)} 条数据")

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
    parser = argparse.ArgumentParser(
        description='量化交易回测系统 - 增强版 (支持多数据源)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用默认数据源 (yahoo优先,失败则用mock)
  python main_enhanced.py --symbol AAPL

  # 强制使用模拟数据
  python main_enhanced.py --symbol AAPL --sources mock

  # 使用特定策略
  python main_enhanced.py --symbol AAPL --strategy macd

  # 多策略对比
  python main_enhanced.py --compare --symbol AAPL

  # 指定数据源
  python main_enhanced.py --symbol AAPL --sources yahoo mock stooq

可用数据源:
  yahoo  - Yahoo Finance (可能需要VPN)
  mock   - 模拟数据 (离线可用)
  stooq  - Stooq (免费,无需API key)
  polygon - Polygon.io (需要API key)
        """
    )

    parser.add_argument('--symbol', type=str, default='AAPL', help='交易标的')
    parser.add_argument('--strategy', type=str, default='moving_average_crossover',
                       choices=['moving_average_crossover', 'mean_reversion', 'momentum',
                               'rsi', 'macd', 'bollinger_bands'],
                       help='选择策略')
    parser.add_argument('--sources', type=str, nargs='+',
                       default=['yahoo', 'mock'],
                       help='数据源列表 (按优先级)')
    parser.add_argument('--period', type=str, default='2y',
                       help='数据时间范围 (1mo, 3mo, 6mo, 1y, 2y, 5y)')
    parser.add_argument('--compare', action='store_true', help='运行多策略对比')

    args = parser.parse_args()

    if args.compare:
        run_multi_strategy_comparison(args.symbol, args.sources)
    else:
        run_backtest(args.symbol, args.strategy, args.sources, args.period)


if __name__ == "__main__":
    main()
