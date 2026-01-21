"""
中文版量化交易主程序
使用Alpha Vantage API
"""

import sys
sys.path.insert(0, '/Users/user/Desktop/量化ai')

import pandas as pd
import numpy as np
from datetime import datetime
import logging
import time

from data_fetcher import DataFetcher
from trading_strategies import (
    MovingAverageCrossover,
    MeanReversion,
    MomentumStrategy,
    RSIStrategy,
    MACDStrategy,
    BollingerBandsStrategy,
)
from backtest_engine import BacktestEngine
from chinese_analytics import ChinesePerformanceAnalyzer
from performance_analytics import save_results_to_csv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_banner():
    """打印欢迎横幅"""
    banner = """
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║           📊 量化交易回测系统 - 中文版 v2.0                        ║
║                                                                   ║
║              使用 Alpha Vantage API 获取真实数据                   ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def create_strategy(strategy_name: str, params: dict = None):
    """创建交易策略"""
    params = params or {}

    strategies = {
        'ma': ('移动平均线交叉', MovingAverageCrossover(
            short_window=params.get('short_window', 20),
            long_window=params.get('long_window', 50)
        )),
        'mean_reversion': ('均值回归', MeanReversion(
            window=params.get('window', 20),
            entry_threshold=params.get('entry_threshold', 2.0),
            exit_threshold=params.get('exit_threshold', 0.5)
        )),
        'momentum': ('动量策略', MomentumStrategy(
            lookback=params.get('lookback', 20),
            threshold=params.get('threshold', 0.02)
        )),
        'rsi': ('RSI策略', RSIStrategy(
            rsi_period=params.get('rsi_period', 14),
            oversold=params.get('oversold', 30),
            overbought=params.get('overbought', 70)
        )),
        'macd': ('MACD策略', MACDStrategy(
            fast=params.get('fast', 12),
            slow=params.get('slow', 26),
            signal=params.get('signal', 9)
        )),
        'bollinger': ('布林带策略', BollingerBandsStrategy(
            window=params.get('window', 20),
            num_std=params.get('num_std', 2.0)
        ))
    }

    if strategy_name not in strategies:
        print(f"\n❌ 未知策略: {strategy_name}")
        print(f"可用策略: {', '.join(strategies.keys())}")
        return None, None

    return strategies[strategy_name][1], strategies[strategy_name][0]


def run_backtest(symbol: str, strategy_name: str = 'ma', period: str = '1y'):
    """运行回测"""

    print(f"\n{'='*80}")
    print(f"开始回测: {symbol}")
    print(f"{'='*80}\n")

    # 步骤1: 获取数据
    print("📡 步骤 1/3: 获取市场数据")
    print("-" * 80)
    print(f"数据源: Alpha Vantage")
    print(f"API Key: RQMP1U6N9J2OMIWH")
    print(f"标的代码: {symbol}")
    print(f"时间范围: {period}")
    print(f"\n⏳ 正在获取数据,请稍候...")

    fetcher = DataFetcher(source="alpha_vantage", api_key="RQMP1U6N9J2OMIWH")
    data = fetcher.fetch_data(symbol, period=period)

    if data.empty:
        print(f"\n❌ 无法获取 {symbol} 的数据")
        print("\n可能的原因:")
        print("  • API调用频率超限 (每分钟5次)")
        print("  • 股票代码不存在")
        print("  • 网络连接问题")
        return None

    print(f"\n✅ 成功获取 {len(data)} 条数据")
    print(f"   日期范围: {data['datetime'].iloc[0]} 到 {data['datetime'].iloc[-1]}")

    # 确保close列是数值类型
    data['close'] = pd.to_numeric(data['close'], errors='coerce')
    print(f"   价格范围: {data['close'].min():.2f} - {data['close'].max():.2f}")

    # 步骤2: 创建策略
    print(f"\n🎯 步骤 2/3: 创建交易策略")
    print("-" * 80)

    strategy, strategy_cn_name = create_strategy(strategy_name)
    if strategy is None:
        return None

    print(f"策略名称: {strategy_cn_name}")
    print(f"策略参数: {strategy.parameters}")

    # 步骤3: 运行回测
    print(f"\n⚙️ 步骤 3/3: 执行回测")
    print("-" * 80)

    initial_capital = 100000
    commission = 0.001

    print(f"初始资金: ¥{initial_capital:,.2f}")
    print(f"手续费率: {commission:.2%}")

    engine = BacktestEngine(strategy, initial_capital=initial_capital, commission=commission)
    results = engine.run(data, symbol)

    # 生成中文报告
    print(f"\n{'='*80}")
    print(f"回测完成!")
    print(f"{'='*80}\n")

    analyzer = ChinesePerformanceAnalyzer()
    report = analyzer.generate_chinese_report(results)
    print(report)

    # 保存结果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print(f"\n💾 正在保存结果...")

    # 保存CSV数据
    csv_file = f"results/{symbol}_{strategy_name}_{timestamp}.csv"
    save_results_to_csv(results, csv_file)
    print(f"✓ CSV数据: {csv_file}")

    # 生成HTML报告
    html_file = f"results/{symbol}_{strategy_name}_{timestamp}_cn.html"
    analyzer.create_chinese_html_report(results, html_file)
    print(f"✓ HTML报告: {html_file}")

    # 生成图表
    try:
        print(f"\n📊 正在生成图表...")
        equity_file = f"results/{symbol}_{strategy_name}_equity_{timestamp}_cn.png"
        analyzer.plot_chinese_equity_curve(
            results['equity_curve'],
            save_path=equity_file
        )
        print(f"✓ 权益曲线: {equity_file}")

        trades_file = f"results/{symbol}_{strategy_name}_trades_{timestamp}_cn.png"
        analyzer.plot_chinese_trades(results['trades'], save_path=trades_file)
        print(f"✓ 交易分析: {trades_file}")

    except Exception as e:
        logger.warning(f"生成图表时出错: {str(e)}")

    return results


def main():
    """主函数"""
    print_banner()

    print("\n📋 使用说明:")
    print("  本系统使用Alpha Vantage API获取真实美股数据")
    print("  API限制: 每分钟5次请求,每天25次,每月500次")
    print("  系统已添加12秒延迟以避免超限\n")

    import argparse
    parser = argparse.ArgumentParser(description='量化交易回测系统')
    parser.add_argument('--symbol', type=str, default='AAPL', help='股票代码 (如: AAPL, MSFT, GOOGL)')
    parser.add_argument('--strategy', type=str, default='ma',
                       choices=['ma', 'mean_reversion', 'momentum', 'rsi', 'macd', 'bollinger'],
                       help='交易策略')
    parser.add_argument('--period', type=str, default='1y',
                       choices=['1mo', '3mo', '6mo', '1y', '2y'],
                       help='数据时间范围')

    args = parser.parse_args()

    # 策略名称映射
    strategy_names = {
        'ma': '移动平均线交叉',
        'mean_reversion': '均值回归',
        'momentum': '动量策略',
        'rsi': 'RSI策略',
        'macd': 'MACD策略',
        'bollinger': '布林带策略'
    }

    print(f"\n📊 回测配置:")
    print(f"  标的代码: {args.symbol}")
    print(f"  交易策略: {strategy_names[args.strategy]}")
    print(f"  时间范围: {args.period}")

    # 运行回测
    results = run_backtest(args.symbol, args.strategy, args.period)

    if results:
        print(f"\n{'='*80}")
        print(f"✅ 回测完成! 结果已保存到 results/ 目录")
        print(f"{'='*80}\n")

        print(f"💡 下一步:")
        print(f"  • 查看HTML报告: open results/*_{args.symbol}_*_cn.html")
        print(f"  • 查看图表: open results/*_{args.symbol}_*_cn.png")
        print(f"  • 查看CSV数据: cat results/*.csv")
    else:
        print(f"\n❌ 回测失败,请检查配置后重试")


if __name__ == "__main__":
    main()
