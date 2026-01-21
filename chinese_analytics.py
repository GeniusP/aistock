"""
中文性能分析模块
优化的回测报告和可视化
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional
import logging
from datetime import datetime
from scipy import stats

logger = logging.getLogger(__name__)

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'STHeiti']
plt.rcParams['axes.unicode_minus'] = False

# 设置中文列名映射
COLUMN_NAMES_CN = {
    'datetime': '日期',
    'open': '开盘价',
    'high': '最高价',
    'low': '最低价',
    'close': '收盘价',
    'volume': '成交量',
    'returns': '收益率',
    'cum_returns': '累计收益',
    'drawdown': '回撤',
    'portfolio_value': '账户价值',
    'cash': '现金',
    'signal': '信号'
}


class ChinesePerformanceAnalyzer:
    """中文性能分析类"""

    @staticmethod
    def generate_chinese_report(results: Dict) -> str:
        """生成中文格式的性能报告"""

        report = []
        report.append("═" * 80)
        report.append("                    量化交易策略回测报告")
        report.append("═" * 80)
        report.append(f"生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
        report.append("")

        # 策略信息
        report.append("【策略信息】")
        report.append(f"策略名称: {results.get('strategy_name', 'N/A')}")
        report.append("")

        # 收益指标
        report.append("【收益指标】")
        report.append(f"初始资金: ¥{results.get('initial_capital', 0):,.2f}")
        report.append(f"最终资金: ¥{results.get('final_value', 0):,.2f}")
        profit_loss = results.get('final_value', 0) - results.get('initial_capital', 0)
        report.append(f"总收益: ¥{profit_loss:,.2f}")
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
        report.append(f"总交易次数: {results.get('total_trades', 0)}笔")
        report.append(f"盈利交易: {results.get('winning_trades', 0)}笔")
        report.append(f"亏损交易: {results.get('losing_trades', 0)}笔")
        report.append(f"胜率: {results.get('win_rate', 0):.2%}")
        report.append(f"平均盈利: ¥{results.get('avg_win', 0):,.2f}")
        report.append(f"平均亏损: ¥{results.get('avg_loss', 0):,.2f}")
        report.append(f"盈亏比: {results.get('profit_factor', 0):.2f}")
        report.append("")

        # 新增量化指标
        if 'equity_curve' in results:
            equity_curve = results['equity_curve']
            if not equity_curve.empty:
                advanced_metrics = ChinesePerformanceAnalyzer.calculate_advanced_metrics(equity_curve)
                report.append("【高级量化指标】")
                report.append(f"年化收益率: {advanced_metrics.get('annual_return', 0):.2%}")
                report.append(f"月度收益率: {advanced_metrics.get('monthly_return', 0):.2%}")
                report.append(f"波动率: {advanced_metrics.get('volatility', 0):.2%}")
                report.append(f"下行风险: {advanced_metrics.get('downside_risk', 0):.2%}")
                report.append(f"索提诺比率: {advanced_metrics.get('sortino_ratio', 0):.2f}")
                report.append(f"卡玛比率: {advanced_metrics.get('calmar_ratio', 0):.2f}")
                report.append(f"VaR (95%): {advanced_metrics.get('var_95', 0):.2%}")
                report.append(f"CVaR (95%): {advanced_metrics.get('cvar_95', 0):.2%}")
                report.append(f"信息比率: {advanced_metrics.get('information_ratio', 0):.2f}")
                report.append(f"偏度: {advanced_metrics.get('skewness', 0):.2f}")
                report.append(f"峰度: {advanced_metrics.get('kurtosis', 0):.2f}")
                report.append("")

        report.append("═" * 80)

        return "\n".join(report)

    @staticmethod
    def calculate_advanced_metrics(equity_curve: pd.DataFrame) -> Dict:
        """计算高级量化指标"""

        if equity_curve.empty or 'portfolio_value' not in equity_curve.columns:
            return {}

        # 计算日收益率
        equity_curve['returns'] = equity_curve['portfolio_value'].pct_change()
        returns = equity_curve['returns'].dropna()

        # 基本参数
        trading_days = len(returns)
        years = trading_days / 252

        # 年化收益率
        initial_value = equity_curve['portfolio_value'].iloc[0]
        final_value = equity_curve['portfolio_value'].iloc[-1]
        total_return = (final_value - initial_value) / initial_value
        annual_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0

        # 月度收益率
        monthly_return = (1 + annual_return) ** (1/12) - 1

        # 波动率
        volatility = returns.std() * np.sqrt(252)

        # 下行风险 (负收益的标准差)
        negative_returns = returns[returns < 0]
        downside_risk = negative_returns.std() * np.sqrt(252) if len(negative_returns) > 0 else 0

        # 索提诺比率
        risk_free_rate = 0.03  # 假设无风险利率3%
        excess_returns = returns - risk_free_rate / 252
        downside_excess = excess_returns[excess_returns < 0]

        if len(downside_excess) > 0 and downside_excess.std() != 0:
            sortino_ratio = np.sqrt(252) * excess_returns.mean() / downside_excess.std()
        else:
            sortino_ratio = 0

        # 卡玛比率
        max_drawdown = ChinesePerformanceAnalyzer.calculate_max_drawdown_series(equity_curve['portfolio_value'])
        calmar_ratio = annual_return / abs(max_drawdown) if max_drawdown != 0 else 0

        # VaR和CVaR (95%置信度)
        var_95 = np.percentile(returns, 5)
        cvar_95 = returns[returns <= var_95].mean()

        # 信息比率 (相对于买入持有)
        benchmark_returns = equity_curve['returns']
        if benchmark_returns.std() != 0:
            information_ratio = np.sqrt(252) * (returns.mean() - benchmark_returns.mean()) / (returns - benchmark_returns).std()
        else:
            information_ratio = 0

        # 偏度和峰度
        skewness = stats.skew(returns)
        kurtosis = stats.kurtosis(returns)

        return {
            'annual_return': annual_return,
            'monthly_return': monthly_return,
            'volatility': volatility,
            'downside_risk': downside_risk,
            'sortino_ratio': sortino_ratio,
            'calmar_ratio': calmar_ratio,
            'var_95': var_95,
            'cvar_95': cvar_95,
            'information_ratio': information_ratio,
            'skewness': skewness,
            'kurtosis': kurtosis
        }

    @staticmethod
    def calculate_max_drawdown_series(series: pd.Series) -> float:
        """计算最大回撤"""
        cummax = series.cummax()
        drawdown = (series - cummax) / cummax
        return drawdown.min()

    @staticmethod
    def plot_chinese_equity_curve(equity_curve: pd.DataFrame,
                                  benchmark: Optional[pd.Series] = None,
                                  save_path: Optional[str] = None):
        """绘制中文权益曲线"""

        if equity_curve.empty:
            logger.warning("没有数据可绘制")
            return

        fig = plt.figure(figsize=(16, 10))

        # 1. 账户价值曲线
        ax1 = plt.subplot(3, 2, 1)
        ax1.plot(equity_curve['date'] if 'date' in equity_curve.columns else equity_curve.index,
                equity_curve['portfolio_value'], label='策略净值', linewidth=2, color='#2E86DE')
        if benchmark is not None:
            normalized_benchmark = (1 + benchmark).cumprod() * equity_curve['portfolio_value'].iloc[0]
            ax1.plot(equity_curve.index, normalized_benchmark, label='基准', linewidth=2, color='#EE5A6F', alpha=0.7)
        ax1.set_title('账户净值曲线', fontsize=14, fontweight='bold')
        ax1.set_xlabel('日期')
        ax1.set_ylabel('账户价值 (¥)')
        ax1.legend(loc='best')
        ax1.grid(True, alpha=0.3)
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'¥{x:,.0f}'))

        # 2. 回撤图
        ax2 = plt.subplot(3, 2, 2)
        if 'portfolio_value' in equity_curve.columns:
            cummax = equity_curve['portfolio_value'].cummax()
            drawdown = (equity_curve['portfolio_value'] - cummax) / cummax * 100
            ax2.fill_between(range(len(drawdown)), drawdown, 0, alpha=0.3, color='#FF6B6B')
            ax2.plot(range(len(drawdown)), drawdown, color='#EE5A6F', linewidth=1)
            ax2.set_title('回撤曲线', fontsize=14, fontweight='bold')
            ax2.set_xlabel('交易日')
            ax2.set_ylabel('回撤 (%)')
            ax2.grid(True, alpha=0.3)

        # 3. 日收益率分布
        ax3 = plt.subplot(3, 2, 3)
        if 'returns' not in equity_curve.columns:
            equity_curve['returns'] = equity_curve['portfolio_value'].pct_change()
        returns = equity_curve['returns'].dropna() * 100
        ax3.hist(returns, bins=50, edgecolor='black', alpha=0.7, color='#54A0FF')
        ax3.axvline(returns.mean(), color='red', linestyle='--', linewidth=2, label=f'均值: {returns.mean():.3f}%')
        ax3.set_title('日收益率分布', fontsize=14, fontweight='bold')
        ax3.set_xlabel('日收益率 (%)')
        ax3.set_ylabel('频数')
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        # 4. 累计收益率
        ax4 = plt.subplot(3, 2, 4)
        cumulative_returns = (1 + equity_curve['returns']).cumprod() * 100 - 100
        ax4.plot(range(len(cumulative_returns)), cumulative_returns, linewidth=2, color='#1DD1A1')
        ax4.fill_between(range(len(cumulative_returns)), cumulative_returns, alpha=0.3, color='#1DD1A1')
        ax4.set_title('累计收益率', fontsize=14, fontweight='bold')
        ax4.set_xlabel('交易日')
        ax4.set_ylabel('累计收益率 (%)')
        ax4.grid(True, alpha=0.3)
        ax4.axhline(0, color='black', linestyle='-', linewidth=0.5)

        # 5. 收益率箱线图
        ax5 = plt.subplot(3, 2, 5)
        monthly_data = equity_curve['returns'].dropna()
        box_data = [monthly_data.sample(min(252, len(monthly_data))) if len(monthly_data) > 252 else monthly_data]
        bp = ax5.boxplot(box_data, labels=['策略'], patch_artist=True)
        bp['boxes'][0].set_facecolor('#54A0FF')
        bp['boxes'][0].set_alpha(0.7)
        ax5.set_title('收益率分布箱线图', fontsize=14, fontweight='bold')
        ax5.set_ylabel('日收益率')
        ax5.grid(True, alpha=0.3)

        # 6. 滚动夏普比率 (252天窗口)
        ax6 = plt.subplot(3, 2, 6)
        if len(equity_curve) > 252:
            rolling_sharpe = equity_curve['returns'].rolling(252).apply(
                lambda x: x.mean() / x.std() * np.sqrt(252) if x.std() != 0 else 0
            )
            ax6.plot(range(len(rolling_sharpe)), rolling_sharpe, linewidth=1.5, color='#Feca57')
            ax6.set_title('滚动夏普比率 (252天)', fontsize=14, fontweight='bold')
            ax6.set_xlabel('交易日')
            ax6.set_ylabel('夏普比率')
            ax6.grid(True, alpha=0.3)
            ax6.axhline(0, color='black', linestyle='-', linewidth=0.5)
        else:
            ax6.text(0.5, 0.5, '数据不足', ha='center', va='center', fontsize=12)
            ax6.set_title('滚动夏普比率', fontsize=14, fontweight='bold')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"图表已保存到 {save_path}")

        plt.show()

    @staticmethod
    def plot_chinese_trades(trades: List, save_path: Optional[str] = None):
        """绘制中文交易分析"""

        if not trades:
            logger.warning("没有交易数据可分析")
            return

        fig = plt.figure(figsize=(16, 10))

        # 准备数据
        trade_data = pd.DataFrame([{
            '盈亏': trade.pnl,
            '收益率': trade.pnl_pct,
            '入场日期': trade.entry_date,
            '出场日期': trade.exit_date,
            '持仓天数': (trade.exit_date - trade.entry_date).days if trade.exit_date else 0
        } for trade in trades if trade.exit_date and trade.pnl is not None])

        if trade_data.empty:
            logger.warning("没有已完成的交易")
            return

        # 1. 盈亏序列
        ax1 = plt.subplot(3, 2, 1)
        colors = ['green' if pnl > 0 else 'red' for pnl in trade_data['盈亏']]
        ax1.bar(range(len(trade_data)), trade_data['盈亏'], color=colors, alpha=0.7)
        ax1.axhline(0, color='black', linestyle='-', linewidth=1)
        ax1.set_title('交易盈亏序列', fontsize=14, fontweight='bold')
        ax1.set_xlabel('交易序号')
        ax1.set_ylabel('盈亏金额 (¥)')
        ax1.grid(True, alpha=0.3)
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'¥{x:,.0f}'))

        # 2. 收益率分布
        ax2 = plt.subplot(3, 2, 2)
        returns_pct = trade_data['收益率'] * 100
        ax2.hist(returns_pct, bins=20, edgecolor='black', alpha=0.7, color='#54A0FF')
        ax2.axvline(0, color='red', linestyle='--', linewidth=2)
        ax2.set_title('交易收益率分布', fontsize=14, fontweight='bold')
        ax2.set_xlabel('收益率 (%)')
        ax2.set_ylabel('频数')
        ax2.grid(True, alpha=0.3)

        # 3. 累计盈亏
        ax3 = plt.subplot(3, 2, 3)
        cumulative_pnl = trade_data['盈亏'].cumsum()
        ax3.plot(range(len(cumulative_pnl)), cumulative_pnl, linewidth=2, color='#1DD1A1')
        ax3.fill_between(range(len(cumulative_pnl)), cumulative_pnl, alpha=0.3, color='#1DD1A1')
        ax3.axhline(0, color='black', linestyle='-', linewidth=1)
        ax3.set_title('累计盈亏曲线', fontsize=14, fontweight='bold')
        ax3.set_xlabel('交易序号')
        ax3.set_ylabel('累计盈亏 (¥)')
        ax3.grid(True, alpha=0.3)
        ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'¥{x:,.0f}'))

        # 4. 持仓天数分析
        ax4 = plt.subplot(3, 2, 4)
        holding_colors = ['green' if pnl > 0 else 'red' for pnl in trade_data['盈亏']]
        ax4.scatter(trade_data['持仓天数'], trade_data['收益率'] * 100,
                   c=holding_colors, alpha=0.6, s=100)
        ax4.set_title('持仓天数 vs 收益率', fontsize=14, fontweight='bold')
        ax4.set_xlabel('持仓天数')
        ax4.set_ylabel('收益率 (%)')
        ax4.grid(True, alpha=0.3)
        ax4.axhline(0, color='black', linestyle='-', linewidth=1)

        # 5. 盈亏饼图
        ax5 = plt.subplot(3, 2, 5)
        winning_trades = trade_data[trade_data['盈亏'] > 0]
        losing_trades = trade_data[trade_data['盈亏'] <= 0]

        pie_data = [
            winning_trades['盈亏'].sum() if len(winning_trades) > 0 else 0,
            abs(losing_trades['盈亏'].sum()) if len(losing_trades) > 0 else 0
        ]
        pie_labels = [f'盈利\n¥{pie_data[0]:,.0f}' if pie_data[0] > 0 else '盈利 ¥0',
                     f'亏损\n¥{pie_data[1]:,.0f}' if pie_data[1] > 0 else '亏损 ¥0']
        pie_colors = ['#26DE81', '#FF6B6B']

        ax5.pie(pie_data, labels=pie_labels, colors=pie_colors, autopct='%1.1f%%',
               startangle=90, textprops={'fontsize': 11, 'weight': 'bold'})
        ax5.set_title('盈亏构成', fontsize=14, fontweight='bold')

        # 6. 交易统计
        ax6 = plt.subplot(3, 2, 6)
        ax6.axis('off')

        stats_text = f"""
        交易统计
        ══════════

        总交易次数: {len(trade_data)}笔
        盈利交易: {len(winning_trades)}笔
        亏损交易: {len(losing_trades)}笔
        胜率: {len(winning_trades)/len(trade_data)*100:.1f}%

        平均盈利: ¥{winning_trades['盈亏'].mean():,.2f}  if len(winning_trades) > 0 else 0
        平均亏损: ¥{losing_trades['盈亏'].mean():,.2f}  if len(losing_trades) > 0 else 0

        最大盈利: ¥{trade_data['盈亏'].max():,.2f}
        最大亏损: ¥{trade_data['盈亏'].min():,.2f}

        平均持仓天数: {trade_data['持仓天数'].mean():.1f}天

        总盈亏: ¥{trade_data['盈亏'].sum():,.2f}
        盈亏比: {abs(winning_trades['盈亏'].sum() / losing_trades['盈亏'].sum()) if losing_trades['盈亏'].sum() != 0 else float('inf'):.2f}
        """

        ax6.text(0.1, 0.9, stats_text, transform=ax6.transAxes,
                fontsize=10, verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"交易分析图已保存到 {save_path}")

        plt.show()

    @staticmethod
    def create_chinese_html_report(results: Dict, output_path: str):
        """创建中文HTML报告"""

        total_return = results.get('total_return', 0)
        final_value = results.get('final_value', 0)
        initial_capital = results.get('initial_capital', 0)

        # 计算高级指标
        advanced_metrics = {}
        if 'equity_curve' in results:
            advanced_metrics = ChinesePerformanceAnalyzer.calculate_advanced_metrics(results['equity_curve'])

        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>量化交易策略回测报告</title>
            <style>
                body {{
                    font-family: 'Microsoft YaHei', 'SimHei', Arial, sans-serif;
                    margin: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 40px;
                    border-radius: 15px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                }}
                h1 {{
                    color: #667eea;
                    font-size: 36px;
                    text-align: center;
                    margin-bottom: 10px;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
                }}
                .subtitle {{
                    text-align: center;
                    color: #666;
                    margin-bottom: 40px;
                    font-size: 16px;
                }}
                .section {{
                    margin-bottom: 35px;
                    padding: 25px;
                    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                    border-radius: 10px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }}
                h2 {{
                    color: #333;
                    margin-top: 0;
                    margin-bottom: 20px;
                    font-size: 24px;
                    border-bottom: 3px solid #667eea;
                    padding-bottom: 10px;
                }}
                .metric-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin-top: 20px;
                }}
                .metric {{
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    transition: transform 0.3s;
                }}
                .metric:hover {{
                    transform: translateY(-5px);
                    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                }}
                .metric-label {{
                    font-size: 14px;
                    color: #666;
                    margin-bottom: 8px;
                }}
                .metric-value {{
                    font-size: 28px;
                    font-weight: bold;
                    color: #333;
                }}
                .positive {{ color: #26DE81; }}
                .negative {{ color: #FF6B6B; }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                    background: white;
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                th {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 15px;
                    text-align: left;
                    font-weight: bold;
                }}
                td {{
                    padding: 12px 15px;
                    border-bottom: 1px solid #ddd;
                }}
                tr:hover {{
                    background-color: #f5f5f5;
                }}
                tr:last-child td {{
                    border-bottom: none;
                }}
                .badge {{
                    display: inline-block;
                    padding: 5px 10px;
                    border-radius: 5px;
                    font-size: 12px;
                    font-weight: bold;
                }}
                .badge-success {{
                    background-color: #26DE81;
                    color: white;
                }}
                .badge-danger {{
                    background-color: #FF6B6B;
                    color: white;
                }}
                .badge-info {{
                    background-color: #54A0FF;
                    color: white;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📊 量化交易策略回测报告</h1>
                <p class="subtitle">生成时间: {timestamp}</p>

                <div class="section">
                    <h2>📈 收益指标</h2>
                    <div class="metric-grid">
                        <div class="metric">
                            <div class="metric-label">初始资金</div>
                            <div class="metric-value">¥{initial_capital:,.2f}</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">最终资金</div>
                            <div class="metric-value">¥{final_value:,.2f}</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">总收益率</div>
                            <div class="metric-value {return_class}">{total_return:.2%}</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">买入持有收益率</div>
                            <div class="metric-value">{buy_hold_return:.2%}</div>
                        </div>
                    </div>
                </div>

                <div class="section">
                    <h2>⚠️ 风险指标</h2>
                    <div class="metric-grid">
                        <div class="metric">
                            <div class="metric-label">夏普比率</div>
                            <div class="metric-value">{sharpe_ratio:.2f}</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">最大回撤</div>
                            <div class="metric-value negative">{max_drawdown:.2%}</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">年化收益率</div>
                            <div class="metric-value {positive_class}">{annual_return:.2%}</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">波动率</div>
                            <div class="metric-value">{volatility:.2%}</div>
                        </div>
                    </div>
                </div>

                <div class="section">
                    <h2>💹 交易统计</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>指标</th>
                                <th>数值</th>
                                <th>评价</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>总交易次数</td>
                                <td>{total_trades}笔</td>
                                <td><span class="badge badge-info">活跃度</span></td>
                            </tr>
                            <tr>
                                <td>盈利交易</td>
                                <td>{winning_trades}笔</td>
                                <td><span class="badge badge-success">盈利</span></td>
                            </tr>
                            <tr>
                                <td>亏损交易</td>
                                <td>{losing_trades}笔</td>
                                <td><span class="badge badge-danger">亏损</span></td>
                            </tr>
                            <tr>
                                <td>胜率</td>
                                <td>{win_rate:.2%}</td>
                                <td>{winrate_badge}</td>
                            </tr>
                            <tr>
                                <td>平均盈利</td>
                                <td>¥{avg_win:,.2f}</td>
                                <td><span class="badge badge-success">表现</span></td>
                            </tr>
                            <tr>
                                <td>平均亏损</td>
                                <td>¥{avg_loss:,.2f}</td>
                                <td><span class="badge badge-danger">风险</span></td>
                            </tr>
                            <tr>
                                <td>盈亏比</td>
                                <td>{profit_factor:.2f}</td>
                                <td>{profit_badge}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <div class="section">
                    <h2>🎯 高级量化指标</h2>
                    <div class="metric-grid">
                        <div class="metric">
                            <div class="metric-label">索提诺比率</div>
                            <div class="metric-value">{sortino_ratio:.2f}</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">卡玛比率</div>
                            <div class="metric-value">{calmar_ratio:.2f}</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">VaR (95%)</div>
                            <div class="metric-value negative">{var_95:.2%}</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">CVaR (95%)</div>
                            <div class="metric-value negative">{cvar_95:.2%}</div>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

        # 计算评价徽章
        win_rate = results.get('win_rate', 0)
        profit_factor = results.get('profit_factor', 0)

        if win_rate >= 0.5:
            winrate_badge = '<span class="badge badge-success">良好</span>'
        else:
            winrate_badge = '<span class="badge badge-danger">需改进</span>'

        if profit_factor >= 2:
            profit_badge = '<span class="badge badge-success">优秀</span>'
        elif profit_factor >= 1:
            profit_badge = '<span class="badge badge-info">良好</span>'
        else:
            profit_badge = '<span class="badge badge-danger">风险高</span>'

        html_content = html_template.format(
            timestamp=datetime.now().strftime('%Y年%m月%d日 %H:%M:%S'),
            initial_capital=initial_capital,
            final_value=final_value,
            total_return=total_return,
            return_class='positive' if total_return >= 0 else 'negative',
            buy_hold_return=results.get('buy_hold_return', 0),
            sharpe_ratio=results.get('sharpe_ratio', 0),
            max_drawdown=results.get('max_drawdown', 0),
            annual_return=advanced_metrics.get('annual_return', 0),
            volatility=advanced_metrics.get('volatility', 0),
            positive_class='positive' if advanced_metrics.get('annual_return', 0) >= 0 else 'negative',
            total_trades=results.get('total_trades', 0),
            winning_trades=results.get('winning_trades', 0),
            losing_trades=results.get('losing_trades', 0),
            win_rate=win_rate,
            avg_win=results.get('avg_win', 0),
            avg_loss=results.get('abs', 0),
            profit_factor=profit_factor,
            winrate_badge=winrate_badge,
            profit_badge=profit_badge,
            sortino_ratio=advanced_metrics.get('sortino_ratio', 0),
            calmar_ratio=advanced_metrics.get('calmar_ratio', 0),
            var_95=advanced_metrics.get('var_95', 0),
            cvar_95=advanced_metrics.get('cvar_95', 0)
        )

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        logger.info(f"中文HTML报告已保存到 {output_path}")


# 向后兼容的别名
PerformanceAnalyzer = ChinesePerformanceAnalyzer
