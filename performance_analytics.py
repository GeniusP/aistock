"""
性能分析和可视化模块
生成回测报告和图表
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False


class PerformanceAnalyzer:
    """性能分析类"""

    @staticmethod
    def generate_report(results: Dict) -> str:
        """
        生成文本格式的性能报告

        Args:
            results: 回测结果字典

        Returns:
            格式化的报告文本
        """
        report = []
        report.append("=" * 80)
        report.append("量化交易策略回测报告")
        report.append("=" * 80)
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # 策略信息
        report.append("【策略信息】")
        report.append(f"策略名称: {results.get('strategy_name', 'N/A')}")
        report.append("")

        # 收益指标
        report.append("【收益指标】")
        report.append(f"初始资金: ${results.get('initial_capital', 0):,.2f}")
        report.append(f"最终资金: ${results.get('final_value', 0):,.2f}")
        report.append(f"总收益: ${results.get('final_value', 0) - results.get('initial_capital', 0):,.2f}")
        report.append(f"总收益率: {results.get('total_return', 0):.2%}")
        report.append(f"买入持有收益率: {results.get('buy_hold_return', 0):.2%}")
        report.append("")

        # 风险指标
        report.append("【风险指标】")
        report.append(f"夏普比率: {results.get('sharpe_ratio', 0):.2f}")
        report.append(f"最大回撤: {results.get('max_drawdown', 0):.2%}")
        report.append("")

        # 交易统计
        report.append("【交易统计】")
        report.append(f"总交易次数: {results.get('total_trades', 0)}")
        report.append(f"盈利交易: {results.get('winning_trades', 0)}")
        report.append(f"亏损交易: {results.get('losing_trades', 0)}")
        report.append(f"胜率: {results.get('win_rate', 0):.2%}")
        report.append(f"平均盈利: ${results.get('avg_win', 0):,.2f}")
        report.append(f"平均亏损: ${results.get('avg_loss', 0):,.2f}")
        report.append(f"盈亏比: {results.get('profit_factor', 0):.2f}")
        report.append("")

        report.append("=" * 80)

        return "\n".join(report)

    @staticmethod
    def plot_equity_curve(equity_curve: pd.DataFrame, benchmark: Optional[pd.Series] = None, save_path: Optional[str] = None):
        """
        绘制权益曲线

        Args:
            equity_curve: 权益曲线数据
            benchmark: 基准收益序列 (可选)
            save_path: 保存路径 (可选)
        """
        plt.figure(figsize=(14, 8))

        # 策略权益曲线
        plt.subplot(2, 2, 1)
        plt.plot(equity_curve['date'], equity_curve['portfolio_value'], label='Strategy', linewidth=2)
        if benchmark is not None:
            normalized_benchmark = (1 + benchmark).cumprod() * equity_curve['portfolio_value'].iloc[0]
            plt.plot(equity_curve['date'], normalized_benchmark, label='Benchmark', linewidth=2, alpha=0.7)
        plt.title('Equity Curve', fontsize=14, fontweight='bold')
        plt.xlabel('Date')
        plt.ylabel('Portfolio Value ($)')
        plt.legend()
        plt.grid(True, alpha=0.3)

        # 回撤图
        plt.subplot(2, 2, 2)
        if 'drawdown' in equity_curve.columns:
            plt.fill_between(equity_curve['date'], equity_curve['drawdown'] * 100, 0, alpha=0.3, color='red')
            plt.plot(equity_curve['date'], equity_curve['drawdown'] * 100, color='red', linewidth=1)
        plt.title('Drawdown', fontsize=14, fontweight='bold')
        plt.xlabel('Date')
        plt.ylabel('Drawdown (%)')
        plt.grid(True, alpha=0.3)

        # 日收益分布
        plt.subplot(2, 2, 3)
        if 'daily_return' in equity_curve.columns:
            returns = equity_curve['daily_return'].dropna()
            plt.hist(returns * 100, bins=50, edgecolor='black', alpha=0.7)
            plt.axvline(returns.mean() * 100, color='red', linestyle='--', linewidth=2, label=f'Mean: {returns.mean()*100:.3f}%')
            plt.title('Daily Returns Distribution', fontsize=14, fontweight='bold')
            plt.xlabel('Daily Return (%)')
            plt.ylabel('Frequency')
            plt.legend()
            plt.grid(True, alpha=0.3)

        # 累计收益
        plt.subplot(2, 2, 4)
        if 'daily_return' in equity_curve.columns:
            cumulative_returns = (1 + equity_curve['daily_return']).cumprod()
            plt.plot(equity_curve['date'], (cumulative_returns - 1) * 100, linewidth=2, color='green')
            plt.title('Cumulative Returns', fontsize=14, fontweight='bold')
            plt.xlabel('Date')
        plt.ylabel('Cumulative Return (%)')
        plt.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"图表已保存到 {save_path}")

        plt.show()

    @staticmethod
    def plot_trade_analysis(trades: List, save_path: Optional[str] = None):
        """
        绘制交易分析图

        Args:
            trades: 交易列表
            save_path: 保存路径 (可选)
        """
        if not trades:
            logger.warning("没有交易数据可分析")
            return

        # 准备数据
        trade_data = pd.DataFrame([{
            'pnl': trade.pnl,
            'pnl_pct': trade.pnl_pct,
            'entry_date': trade.entry_date,
            'exit_date': trade.exit_date
        } for trade in trades])

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # 盈亏分布
        ax1 = axes[0, 0]
        colors = ['green' if pnl > 0 else 'red' for pnl in trade_data['pnl']]
        ax1.bar(range(len(trade_data)), trade_data['pnl'], color=colors, alpha=0.7)
        ax1.axhline(0, color='black', linestyle='-', linewidth=0.5)
        ax1.set_title('Trade P&L', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Trade Number')
        ax1.set_ylabel('P&L ($)')
        ax1.grid(True, alpha=0.3)

        # 盈亏百分比分布
        ax2 = axes[0, 1]
        ax2.hist(trade_data['pnl_pct'] * 100, bins=30, edgecolor='black', alpha=0.7)
        ax2.axvline(0, color='red', linestyle='--', linewidth=2)
        ax2.set_title('Return Distribution', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Return (%)')
        ax2.set_ylabel('Frequency')
        ax2.grid(True, alpha=0.3)

        # 累计盈利
        ax3 = axes[1, 0]
        cumulative_pnl = trade_data['pnl'].cumsum()
        ax3.plot(range(len(cumulative_pnl)), cumulative_pnl, linewidth=2, color='blue')
        ax3.fill_between(range(len(cumulative_pnl)), cumulative_pnl, alpha=0.3)
        ax3.axhline(0, color='black', linestyle='-', linewidth=0.5)
        ax3.set_title('Cumulative P&L', fontsize=14, fontweight='bold')
        ax3.set_xlabel('Trade Number')
        ax3.set_ylabel('Cumulative P&L ($)')
        ax3.grid(True, alpha=0.3)

        # 盈亏统计
        ax4 = axes[1, 1]
        winning_trades = trade_data[trade_data['pnl'] > 0]
        losing_trades = trade_data[trade_data['pnl'] <= 0]

        stats = [
            f'Total Trades: {len(trade_data)}',
            f'Winning Trades: {len(winning_trades)}',
            f'Losing Trades: {len(losing_trades)}',
            f'Win Rate: {len(winning_trades)/len(trade_data)*100:.1f}%',
            f'Total P&L: ${trade_data["pnl"].sum():,.2f}',
            f'Avg Win: ${winning_trades["pnl"].mean():,.2f}' if len(winning_trades) > 0 else 'Avg Win: N/A',
            f'Avg Loss: ${losing_trades["pnl"].mean():,.2f}' if len(losing_trades) > 0 else 'Avg Loss: N/A'
        ]

        ax4.axis('off')
        y_position = 0.9
        for stat in stats:
            ax4.text(0.1, y_position, stat, fontsize=12, transform=ax4.transAxes)
            y_position -= 0.12

        ax4.set_title('Trade Statistics', fontsize=14, fontweight='bold')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"交易分析图已保存到 {save_path}")

        plt.show()

    @staticmethod
    def plot_monthly_returns(returns: pd.Series, save_path: Optional[str] = None):
        """
        绘制月度收益热力图

        Args:
            returns: 日收益率序列
            save_path: 保存路径 (可选)
        """
        # 创建月度收益表
        returns_df = pd.DataFrame(returns)
        returns_df.index = pd.to_datetime(returns_df.index)

        # 计算月度收益
        monthly_returns = returns_df.resample('M').apply(lambda x: (1 + x).prod() - 1)
        monthly_returns = monthly_returns * 100

        # 创建年份和月份的透视表
        monthly_returns_table = pd.DataFrame()
        for ret in monthly_returns.itertuples():
            year = ret.Index.year
            month = ret.Index.month
            month_name = ret.Index.strftime('%b')

            if year not in monthly_returns_table.index:
                monthly_returns_table.loc[year] = [np.nan] * 12

            monthly_returns_table.loc[year, month_name] = ret[0]

        # 绘制热力图
        plt.figure(figsize=(12, 8))
        sns.heatmap(
            monthly_returns_table,
            annot=True,
            fmt='.2f',
            cmap='RdYlGn',
            center=0,
            cbar_kws={'label': 'Return (%)'},
            linewidths=0.5
        )
        plt.title('Monthly Returns Heatmap', fontsize=16, fontweight='bold')
        plt.xlabel('Month')
        plt.ylabel('Year')
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"月度收益热力图已保存到 {save_path}")

        plt.show()


def save_results_to_csv(results: Dict, filepath: str):
    """
    将回测结果保存到CSV文件

    Args:
        results: 回测结果字典
        filepath: 保存路径
    """
    # 保存权益曲线
    if 'equity_curve' in results:
        equity_curve = results['equity_curve']
        equity_curve.to_csv(filepath.replace('.csv', '_equity.csv'), index=False)

    # 保存交易记录
    if 'trades' in results and results['trades']:
        trades_data = []
        for trade in results['trades']:
            trades_data.append({
                'symbol': trade.symbol,
                'entry_date': trade.entry_date,
                'exit_date': trade.exit_date,
                'entry_price': trade.entry_price,
                'exit_price': trade.exit_price,
                'quantity': trade.quantity,
                'pnl': trade.pnl,
                'pnl_pct': trade.pnl_pct
            })

        trades_df = pd.DataFrame(trades_data)
        trades_df.to_csv(filepath.replace('.csv', '_trades.csv'), index=False)

    logger.info(f"结果已保存到 {filepath}")


def create_html_report(results: Dict, output_path: str):
    """
    创建HTML格式的报告

    Args:
        results: 回测结果字典
        output_path: 输出路径
    """
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>量化交易策略回测报告</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background-color: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #333;
                border-bottom: 3px solid #4CAF50;
                padding-bottom: 10px;
            }}
            h2 {{
                color: #555;
                margin-top: 30px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            th, td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            th {{
                background-color: #4CAF50;
                color: white;
            }}
            tr:hover {{
                background-color: #f5f5f5;
            }}
            .metric {{
                display: inline-block;
                margin: 10px;
                padding: 15px;
                background-color: #f9f9f9;
                border-radius: 5px;
                min-width: 200px;
            }}
            .metric-label {{
                font-weight: bold;
                color: #666;
            }}
            .metric-value {{
                font-size: 24px;
                color: #333;
                margin-top: 5px;
            }}
            .positive {{ color: #4CAF50; }}
            .negative {{ color: #f44336; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>量化交易策略回测报告</h1>
            <p>生成时间: {timestamp}</p>

            <h2>策略信息</h2>
            <p><strong>策略名称:</strong> {strategy_name}</p>

            <h2>收益指标</h2>
            <div class="metric">
                <div class="metric-label">初始资金</div>
                <div class="metric-value">${initial_capital:,.2f}</div>
            </div>
            <div class="metric">
                <div class="metric-label">最终资金</div>
                <div class="metric-value">${final_value:,.2f}</div>
            </div>
            <div class="metric">
                <div class="metric-label">总收益率</div>
                <div class="metric-value {return_class}">{total_return:.2%}</div>
            </div>
            <div class="metric">
                <div class="metric-label">买入持有收益率</div>
                <div class="metric-value">{buy_hold_return:.2%}</div>
            </div>

            <h2>风险指标</h2>
            <div class="metric">
                <div class="metric-label">夏普比率</div>
                <div class="metric-value">{sharpe_ratio:.2f}</div>
            </div>
            <div class="metric">
                <div class="metric-label">最大回撤</div>
                <div class="metric-value negative">{max_drawdown:.2%}</div>
            </div>

            <h2>交易统计</h2>
            <table>
                <tr>
                    <th>指标</th>
                    <th>数值</th>
                </tr>
                <tr>
                    <td>总交易次数</td>
                    <td>{total_trades}</td>
                </tr>
                <tr>
                    <td>盈利交易</td>
                    <td>{winning_trades}</td>
                </tr>
                <tr>
                    <td>亏损交易</td>
                    <td>{losing_trades}</td>
                </tr>
                <tr>
                    <td>胜率</td>
                    <td>{win_rate:.2%}</td>
                </tr>
                <tr>
                    <td>平均盈利</td>
                    <td>${avg_win:,.2f}</td>
                </tr>
                <tr>
                    <td>平均亏损</td>
                    <td>${avg_loss:,.2f}</td>
                </tr>
                <tr>
                    <td>盈亏比</td>
                    <td>{profit_factor:.2f}</td>
                </tr>
            </table>
        </div>
    </body>
    </html>
    """

    total_return = results.get('total_return', 0)
    html_content = html_template.format(
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        strategy_name=results.get('strategy_name', 'N/A'),
        initial_capital=results.get('initial_capital', 0),
        final_value=results.get('final_value', 0),
        total_return=total_return,
        return_class='positive' if total_return >= 0 else 'negative',
        buy_hold_return=results.get('buy_hold_return', 0),
        sharpe_ratio=results.get('sharpe_ratio', 0),
        max_drawdown=results.get('max_drawdown', 0),
        total_trades=results.get('total_trades', 0),
        winning_trades=results.get('winning_trades', 0),
        losing_trades=results.get('losing_trades', 0),
        win_rate=results.get('win_rate', 0),
        avg_win=results.get('avg_win', 0),
        avg_loss=results.get('avg_loss', 0),
        profit_factor=results.get('profit_factor', 0)
    )

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    logger.info(f"HTML报告已保存到 {output_path}")


if __name__ == "__main__":
    # 测试代码
    from data_fetcher import DataFetcher
    from backtest_engine import BacktestEngine
    from trading_strategies import MovingAverageCrossover

    # 获取数据并运行回测
    fetcher = DataFetcher()
    data = fetcher.fetch_data("AAPL", period="2y")

    strategy = MovingAverageCrossover(20, 50)
    engine = BacktestEngine(strategy, initial_capital=100000)
    results = engine.run(data, "AAPL")

    # 生成报告
    analyzer = PerformanceAnalyzer()

    print("\n" + analyzer.generate_report(results))

    # 绘制图表
    analyzer.plot_equity_curve(results['equity_curve'])
    analyzer.plot_trade_analysis(results['trades'])

    # 保存结果
    save_results_to_csv(results, "results/backtest_results.csv")
    create_html_report(results, "results/backtest_report.html")
