"""
量化交易系统主程序
整合所有模块,提供完整的交易回测流程
"""

import yaml
import logging
import argparse
from pathlib import Path
from datetime import datetime

from data_fetcher import DataFetcher
from trading_strategies import (
    MovingAverageCrossover,
    MeanReversion,
    MomentumStrategy,
    RSIStrategy,
    MACDStrategy,
    BollingerBandsStrategy,
    MultiIndicatorStrategy
)
from backtest_engine import BacktestEngine
from performance_analytics import PerformanceAnalyzer, save_results_to_csv, create_html_report
from risk_management import RiskManager, KellyCriterionSizer

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/trading_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def load_config(config_path: str = "config.yaml") -> dict:
    """加载配置文件"""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config


def create_strategy(config: dict):
    """根据配置创建策略对象"""
    strategy_name = config['strategy']['name']
    params = config['strategy']['parameters']

    strategy_map = {
        'moving_average_crossover': lambda: MovingAverageCrossover(
            short_window=params.get('short_window', 20),
            long_window=params.get('long_window', 50)
        ),
        'mean_reversion': lambda: MeanReversion(
            window=params.get('window', 20),
            entry_threshold=params.get('entry_threshold', 2.0),
            exit_threshold=params.get('exit_threshold', 0.5)
        ),
        'momentum': lambda: MomentumStrategy(
            lookback=params.get('lookback', 20),
            threshold=params.get('threshold', 0.02)
        ),
        'rsi': lambda: RSIStrategy(
            rsi_period=params.get('rsi_period', 14),
            oversold=params.get('oversold', 30),
            overbought=params.get('overbought', 70)
        ),
        'macd': lambda: MACDStrategy(
            fast=params.get('fast', 12),
            slow=params.get('slow', 26),
            signal=params.get('signal', 9)
        ),
        'bollinger_bands': lambda: BollingerBandsStrategy(
            window=params.get('window', 20),
            num_std=params.get('num_std', 2.0)
        )
    }

    if strategy_name not in strategy_map:
        raise ValueError(f"未知策略: {strategy_name}")

    return strategy_map[strategy_name]()


def run_backtest(config: dict, symbols: list = None):
    """执行回测流程"""

    logger.info("=" * 80)
    logger.info("开始量化交易回测")
    logger.info("=" * 80)

    # 使用配置中的symbols或使用传入的symbols
    test_symbols = symbols or config['data']['symbols']

    # 获取数据
    logger.info("步骤 1/4: 获取市场数据")
    fetcher = DataFetcher(source=config['data']['source'])

    all_results = []

    for symbol in test_symbols:
        logger.info(f"\n正在处理 {symbol}...")

        data = fetcher.fetch_data(
            symbol=symbol,
            interval=config['data']['interval'],
            period=config['data']['period']
        )

        if data.empty:
            logger.warning(f"无法获取 {symbol} 的数据,跳过")
            continue

        # 创建策略
        logger.info(f"步骤 2/4: 创建策略 - {config['strategy']['name']}")
        strategy = create_strategy(config)

        # 运行回测
        logger.info("步骤 3/4: 执行回测")
        engine = BacktestEngine(
            strategy=strategy,
            initial_capital=config['backtest']['initial_capital'],
            commission=config['backtest']['commission'],
            slippage=config['backtest']['slippage']
        )

        results = engine.run(data, symbol)
        all_results.append(results)

        # 生成报告
        logger.info("步骤 4/4: 生成报告")
        analyzer = PerformanceAnalyzer()

        # 打印文本报告
        report = analyzer.generate_report(results)
        print("\n" + report)

        # 保存结果
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if config['output']['save_results']:
            save_results_to_csv(results, f"results/{symbol}_backtest_{timestamp}.csv")

        # 绘制图表
        if config['output']['plot_charts']:
            try:
                analyzer.plot_equity_curve(
                    results['equity_curve'],
                    save_path=f"results/{symbol}_equity_{timestamp}.png"
                )
                analyzer.plot_trade_analysis(
                    results['trades'],
                    save_path=f"results/{symbol}_trades_{timestamp}.png"
                )
            except Exception as e:
                logger.warning(f"绘制图表时出错: {str(e)}")

        # 生成HTML报告
        create_html_report(results, f"results/{symbol}_report_{timestamp}.html")

    # 生成汇总报告
    if len(all_results) > 1:
        generate_summary_report(all_results, test_symbols)

    logger.info("\n" + "=" * 80)
    logger.info("回测完成!")
    logger.info("=" * 80)


def generate_summary_report(all_results: list, symbols: list):
    """生成多标的汇总报告"""

    print("\n" + "=" * 80)
    print("多标的汇总报告")
    print("=" * 80)

    summary_data = []
    for i, results in enumerate(all_results):
        summary_data.append({
            'Symbol': symbols[i],
            'Total Return': f"{results['total_return']:.2%}",
            'Sharpe Ratio': f"{results['sharpe_ratio']:.2f}",
            'Max Drawdown': f"{results['max_drawdown']:.2%}",
            'Win Rate': f"{results['win_rate']:.2%}",
            'Total Trades': results['total_trades']
        })

    summary_df = pd.DataFrame(summary_data)
    print(summary_df.to_string(index=False))

    # 计算平均表现
    avg_return = sum(r['total_return'] for r in all_results) / len(all_results)
    avg_sharpe = sum(r['sharpe_ratio'] for r in all_results) / len(all_results)

    print(f"\n平均收益率: {avg_return:.2%}")
    print(f"平均夏普比率: {avg_sharpe:.2f}")


def run_multi_strategy_comparison(config: dict, symbol: str = "AAPL"):
    """运行多策略对比"""

    logger.info("执行多策略对比分析")

    # 获取数据
    fetcher = DataFetcher(source=config['data']['source'])
    data = fetcher.fetch_data(symbol, period=config['data']['period'])

    if data.empty:
        logger.error(f"无法获取 {symbol} 的数据")
        return

    # 定义多个策略
    strategies = [
        MovingAverageCrossover(20, 50),
        MeanReversion(20, 2.0, 0.5),
        MomentumStrategy(20, 0.02),
        RSIStrategy(14, 30, 70),
        MACDStrategy(12, 26, 9),
        BollingerBandsStrategy(20, 2.0)
    ]

    results_comparison = []

    for strategy in strategies:
        engine = BacktestEngine(
            strategy=strategy,
            initial_capital=config['backtest']['initial_capital'],
            commission=config['backtest']['commission']
        )

        results = engine.run(data, symbol)
        results_comparison.append({
            'Strategy': strategy.name,
            'Return': f"{results['total_return']:.2%}",
            'Sharpe': f"{results['sharpe_ratio']:.2f}",
            'Max DD': f"{results['max_drawdown']:.2%}",
            'Win Rate': f"{results['win_rate']:.2%}"
        })

    # 打印对比结果
    print("\n" + "=" * 80)
    print("策略对比结果")
    print("=" * 80)
    comparison_df = pd.DataFrame(results_comparison)
    print(comparison_df.to_string(index=False))


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='量化交易回测系统')
    parser.add_argument('--config', type=str, default='config.yaml', help='配置文件路径')
    parser.add_argument('--symbol', type=str, help='单个交易标的')
    parser.add_argument('--symbols', type=str, nargs='+', help='多个交易标的')
    parser.add_argument('--compare', action='store_true', help='运行多策略对比')
    parser.add_argument('--strategy', type=str, choices=[
        'moving_average_crossover', 'mean_reversion', 'momentum',
        'rsi', 'macd', 'bollinger_bands'
    ], help='选择策略')

    args = parser.parse_args()

    # 加载配置
    try:
        config = load_config(args.config)
    except FileNotFoundError:
        logger.error(f"配置文件未找到: {args.config}")
        return

    # 创建必要的目录
    Path("data").mkdir(exist_ok=True)
    Path("results").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)

    # 覆盖配置中的策略选择
    if args.strategy:
        config['strategy']['name'] = args.strategy

    # 执行回测或对比
    if args.compare:
        symbol = args.symbol or config['data']['symbols'][0]
        run_multi_strategy_comparison(config, symbol)
    else:
        symbols = args.symbols or config['data']['symbols']
        if args.symbol:
            symbols = [args.symbol]
        run_backtest(config, symbols)


if __name__ == "__main__":
    # 导入pandas用于汇总报告
    import pandas as pd

    main()
