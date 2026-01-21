"""
完全中文化的量化交易系统配置
将所有英文界面元素转换为中文
"""

import matplotlib.pyplot as plt
import matplotlib as mpl
import warnings

# 设置matplotlib中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'STHeiti', 'Heiti TC', 'Songti SC']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 中文名称映射
TERM_CN = {
    # 基础术语
    'Open': '开盘价',
    'High': '最高价',
    'Low': '最低价',
    'Close': '收盘价',
    'Volume': '成交量',
    'Date': '日期',
    'Price': '价格',
    'Returns': '收益率',
    'Signal': '交易信号',

    # 技术指标
    'SMA': '简单移动平均',
    'EMA': '指数移动平均',
    'RSI': '相对强弱指标',
    'MACD': '指数平滑异同移动平均线',
    'BB': '布林带',
    'ATR': '平均真实波幅',
    'OBV': '能量潮',

    # 交易相关
    'Buy': '买入',
    'Sell': '卖出',
    'Hold': '持有',
    'Long': '做多',
    'Short': '做空',
    'Position': '持仓',
    'Portfolio': '投资组合',
    'Capital': '资金',
    'Profit': '利润',
    'Loss': '亏损',

    # 风险指标
    'Sharpe Ratio': '夏普比率',
    'Sortino Ratio': '索提诺比率',
    'Calmar Ratio': '卡玛比率',
    'Max Drawdown': '最大回撤',
    'Volatility': '波动率',
    'VaR': '风险价值',
    'CVaR': '条件风险价值',

    # 性能指标
    'Total Return': '总收益率',
    'Annual Return': '年化收益率',
    'CAGR': '复合年增长率',
    'Win Rate': '胜率',
    'Profit Factor': '盈亏比',
    'Expectancy': '期望收益',
    'Average Win': '平均盈利',
    'Average Loss': '平均亏损',

    # 图表相关
    'Equity Curve': '权益曲线',
    'Drawdown': '回撤',
    'Cumulative Returns': '累计收益',
    'Returns Distribution': '收益率分布',
    'Trade Analysis': '交易分析',
    'P&L': '盈亏',
}

# 颜色方案 - 中国风
COLOR_SCHEME_CN = {
    'up': '#26DE81',      # 上涨 - 绿色
    'down': '#FF6B6B',    # 下跌 - 红色
    'primary': '#54A0FF',  # 主色 - 蓝色
    'background': '#f8f9fa',  # 背景
    'text': '#2d3436',     # 文字
    'grid': '#e0e0e0',     # 网格
    'highlight': '#f1c40f', # 高亮
}


def set_chinese_style():
    """设置中文化样式"""
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        mpl.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'STHeiti']
        mpl.rcParams['axes.unicode_minus'] = False

    print("✓ 已启用中文字体设置")


def get_chinese_term(english_term: str) -> str:
    """获取中文术语"""
    return TERM_CN.get(english_term, english_term)


def translate_formula_name(name: str) -> str:
    """翻译公式名称"""
    formulas = {
        'Sharpe Ratio': '夏普比率',
        'Sortino Ratio': '索提诺比率',
        'Calmar Ratio': '卡玛比率',
        'Information Ratio': '信息比率',
        'Treynor Ratio': '特雷纳比率',
        'Omega Ratio': '欧米伽比率',
        'Beta': '贝塔系数',
        'Alpha': '阿尔法',
        'R-squared': 'R平方',
    }
    return formulas.get(name, name)


def format_chinese_number(value: float, is_currency: bool = False) -> str:
    """格式化中文数字"""
    if is_currency:
        if abs(value) >= 1_000_000_000:
            return f"¥{value/1_000_000_000:.2f}亿元"
        elif abs(value) >= 10_000:
            return f"¥{value/10_000:.2f}万元"
        else:
            return f"¥{value:,.2f}"
    else:
        return f"{value:,.2f}"


def format_chinese_percent(value: float) -> str:
    """格式化中文百分比"""
    return f"{value:.2%}"


def format_chinese_date(date_str: str) -> str:
    """格式化中文日期"""
    try:
        date_obj = pd.to_datetime(date_str)
        return date_obj.strftime('%Y年%m月%d日')
    except:
        return date_str


# 导入pandas用于日期格式化
import pandas as pd


class ChineseUI:
    """中文界面管理类"""

    @staticmethod
    def print_banner():
        """打印中文横幅"""
        print("""
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║              📊 量化交易回测系统 v2.0                                   ║
║                                                                   ║
║                  中文版 | 专业级 | 全功能                               ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
        """)

    @staticmethod
    def print_menu():
        """打印中文菜单"""
        print("\n" + "="*80)
        print("【主菜单】")
        print("="*80)
        print("1. 运行回测     - 执行策略回测并生成报告")
        print("2. 策略对比     - 对比多个策略表现")
        print("3. 查看报告     - 查看历史回测结果")
        print("4. 系统设置     - 配置数据源和参数")
        print("5. 帮助文档     - 查看使用说明")
        print("0. 退出程序")
        print("="*80)

    @staticmethod
    def print_data_menu():
        """打印数据源菜单"""
        print("\n【选择数据源】")
        print("1. Alpha Vantage - 真实美股数据 (推荐)")
        print("2. Yahoo Finance  - 全球市场数据")
        print("3. 模拟数据       - 学习测试使用 (无限制)")

    @staticmethod
    def print_strategy_menu():
        """打印策略菜单"""
        print("\n【选择交易策略】")
        print("1. 移动平均线交叉 (MA Crossover)")
        print("2. 均值回归 (Mean Reversion)")
        print("3. 动量策略 (Momentum)")
        print("4. RSI相对强弱指标")
        print("5. MACD指标")
        print("6. 布林带策略 (Bollinger Bands)")
        print("7. 多指标组合 (Multi-Indicator)")

    @staticmethod
    def print_status_summary(results: dict):
        """打印中文状态摘要"""
        print("\n" + "═"*80)
        print("【回测结果摘要】")
        print("═"*80)

        print(f"\n💰 资金情况:")
        initial = results.get('initial_capital', 0)
        final = results.get('final_value', 0)
        profit = final - initial
        profit_pct = (final - initial) / initial if initial > 0 else 0

        print(f"  初始资金: ¥{initial:,.2f}")
        print(f"  最终资金: ¥{final:,.2f}")
        print(f"  盈亏金额: ¥{profit:,.2f}")
        print(f"  收益率:   {format_chinese_percent(profit_pct)}")

        print(f"\n⚠️ 风险指标:")
        sharpe = results.get('sharpe_ratio', 0)
        max_dd = results.get('max_drawdown', 0)

        print(f"  夏普比率: {sharpe:.2f} ", end="")
        if sharpe > 1:
            print("✓ 优秀")
        elif sharpe > 0.5:
            print("✓ 良好")
        else:
            print("✗ 需改进")

        print(f"  最大回撤: {format_chinese_percent(max_dd)} ", end="")
        if abs(max_dd) < 0.1:
            print("✓ 优秀")
        elif abs(max_dd) < 0.2:
            print("✓ 良好")
        else:
            print("⚠️ 较大")

        print(f"\n📈 交易统计:")
        total = results.get('total_trades', 0)
        winning = results.get('winning_trades', 0)
        losing = results.get('losing_trades', 0)
        win_rate = results.get('win_rate', 0)

        print(f"  总交易: {total}笔")
        print(f"  盈利: {winning}笔")
        print(f"  亏损: {losing}笔")
        print(f"  胜率: {format_chinese_percent(win_rate)}")

        print(f"\n🎯 风险调整收益:")
        if 'equity_curve' in results:
            advanced = ChinesePerformanceAnalyzer.calculate_advanced_metrics(results['equity_curve'])
            print(f"  索提诺比率: {advanced.get('sortino_ratio', 0):.2f}")
            print(f"  卡玛比率:   {advanced.get('calmar_ratio', 0):.2f}")
            print(f"  波动率:     {format_chinese_percent(advanced.get('volatility', 0))}")

        print("\n" + "═"*80)


def demonstrate_chinese_ui():
    """演示中文界面"""

    ChineseUI.print_banner()

    print("\n📋 可用功能:")
    print("  1. 运行单策略回测")
    print("  2. 多策略对比分析")
    print("  3. 查看详细报告")
    print("  4. 导出数据和图表")

    print("\n💡 使用示例:")
    print("  python main_enhanced.py --sources mock --symbol AAPL")
    print("  python main_enhanced.py --compare --symbol AAPL --sources mock")
    print("  python run_chinese_demo.py")

    print("\n📊 系统特点:")
    print("  ✓ 完全中文界面")
    print("  ✓ 17个量化指标")
    print("  ✓ 专业可视化")
    print("  ✓ 一键生成报告")
    print("  ✓ 多数据源支持")

    print("\n" + "="*80)
    print("系统已准备就绪! 🚀")
    print("="*80)


if __name__ == "__main__":
    set_chinese_style()
    demonstrate_chinese_ui()
