# 量化交易系统

一个功能完整的金融量化交易回测框架,支持多种技术指标、交易策略、风险管理和性能分析。

## 功能特性

### 1. 数据获取模块 ([data_fetcher.py](data_fetcher.py))
- 支持Yahoo Finance数据源
- 支持多种时间间隔(分钟、小时、日、周、月)
- 批量数据获取和本地缓存
- 数据保存和加载功能

### 2. 技术指标模块 ([technical_indicators.py](technical_indicators.py))
实现常用技术指标:
- **趋势指标**: SMA, EMA
- **动量指标**: RSI, MACD, Stochastic, Williams %R
- **波动指标**: Bollinger Bands, ATR
- **成交量指标**: OBV
- **其他**: CCI

### 3. 交易策略模块 ([trading_strategies.py](trading_strategies.py))
内置多种策略:
- **移动平均线交叉策略** (MA Crossover)
- **均值回归策略** (Mean Reversion)
- **动量策略** (Momentum)
- **RSI策略**
- **MACD策略**
- **布林带策略** (Bollinger Bands)
- **多指标组合策略** (Multi-Indicator)

### 4. 回测引擎 ([backtest_engine.py](backtest_engine.py))
- 完整的交易模拟
- 手续费和滑点模拟
- 投资组合管理
- 交易记录追踪
- 权益曲线生成

### 5. 风险管理模块 ([risk_management.py](risk_management.py))
**仓位管理**:
- 固定比例法
- 凯利公式法
- ATR基于法
- 波动率目标法

**风险控制**:
- 止损止盈
- 最大回撤限制
- 仓位集中度限制

**风险指标**:
- VaR (风险价值)
- CVaR (条件风险价值)
- 最大回撤
- 夏普比率
- 索提诺比率
- 卡玛比率
- 信息比率

### 6. 性能分析模块 ([performance_analytics.py](performance_analytics.py))
- 详细的回测报告
- 权益曲线可视化
- 交易分析图表
- 月度收益热力图
- HTML格式报告
- CSV数据导出

## 安装依赖

```bash
pip install -r requirements.txt
```

**注意**: TA-Lib需要额外安装,请参考官方文档。

## 快速开始

### 1. 基本使用

```bash
# 使用默认配置回测
python main.py

# 指定单个标的
python main.py --symbol AAPL

# 指定多个标的
python main.py --symbols AAPL MSFT GOOGL

# 选择特定策略
python main.py --symbol AAPL --strategy moving_average_crossover

# 运行多策略对比
python main.py --compare --symbol AAPL
```

### 2. 配置文件

编辑 [config.yaml](config.yaml) 自定义回测参数:

```yaml
# 数据配置
data:
  source: "yahoo"
  symbols:
    - "AAPL"
    - "MSFT"
  interval: "1d"
  period: "2y"

# 策略配置
strategy:
  name: "moving_average_crossover"
  parameters:
    short_window: 20
    long_window: 50
    stop_loss: 0.02
    take_profit: 0.05

# 回测配置
backtest:
  initial_capital: 100000
  commission: 0.001
  slippage: 0.0001

# 风险管理
risk:
  max_position_size: 0.2
  max_total_position: 0.8
  max_drawdown: 0.15
```

### 3. 编程方式使用

```python
from data_fetcher import DataFetcher
from trading_strategies import MovingAverageCrossover
from backtest_engine import BacktestEngine
from performance_analytics import PerformanceAnalyzer

# 获取数据
fetcher = DataFetcher()
data = fetcher.fetch_data("AAPL", period="2y")

# 创建策略
strategy = MovingAverageCrossover(short_window=20, long_window=50)

# 运行回测
engine = BacktestEngine(strategy, initial_capital=100000)
results = engine.run(data, "AAPL")

# 生成报告
analyzer = PerformanceAnalyzer()
print(analyzer.generate_report(results))

# 绘制图表
analyzer.plot_equity_curve(results['equity_curve'])
analyzer.plot_trade_analysis(results['trades'])
```

## 项目结构

```
量化ai/
├── main.py                      # 主程序
├── config.yaml                  # 配置文件
├── requirements.txt             # 依赖包
├── data_fetcher.py             # 数据获取模块
├── technical_indicators.py     # 技术指标模块
├── trading_strategies.py       # 交易策略模块
├── backtest_engine.py          # 回测引擎
├── risk_management.py          # 风险管理模块
├── performance_analytics.py    # 性能分析模块
├── data/                       # 数据目录
├── results/                    # 结果目录
└── logs/                       # 日志目录
```

## 性能指标说明

| 指标 | 说明 |
|-----|------|
| 总收益率 | 策略的累计收益率 |
| 夏普比率 | 风险调整后的收益,越高越好 |
| 最大回撤 | 从峰值到谷值的最大跌幅 |
| 胜率 | 盈利交易占总交易的比例 |
| 盈亏比 | 总盈利与总亏损的比值 |
| 卡玛比率 | 年化收益与最大回撤的比值 |

## 注意事项

1. **历史表现不代表未来**: 回测结果不能保证未来收益
2. **过拟合风险**: 避免过度优化参数
3. **交易成本**: 实际交易中可能存在滑点和额外费用
4. **市场变化**: 市场环境变化可能影响策略有效性
5. **风险控制**: 始终使用止损和仓位管理

## 扩展开发

### 添加新策略

```python
from trading_strategies import BaseStrategy

class MyStrategy(BaseStrategy):
    def generate_signals(self, data):
        # 实现你的信号生成逻辑
        data['signal'] = 0
        # ...你的代码...
        return data
```

### 添加新指标

```python
from technical_indicators import TechnicalIndicators

@staticmethod
def my_indicator(data: pd.Series, window: int = 20) -> pd.Series:
    # 实现你的指标计算逻辑
    return result
```

## 许可证

MIT License

## 贡献

欢迎提交问题和拉取请求!

## 联系方式

如有问题或建议,请提交Issue。
