# 📊 量化交易系统 - 完整版

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

一个功能完整的**金融量化交易回测框架**，采用模块化设计，支持多种技术指标、交易策略、风险管理和性能分析。完全中文化界面，集成Tiingo API，支持A股市场情绪分析。

---

## ✨ 核心特性

### 🎯 完整的量化回测系统
- ✅ **6种交易策略** - MA交叉、均值回归、动量、RSI、MACD、布林带
- ✅ **17个量化指标** - 基础6个 + 高级11个专业指标
- ✅ **完整回测引擎** - 手续费、滑点、仓位管理
- ✅ **风险管理** - 4种仓位管理方法 + VaR/CVaR风险控制

### 🌏 完全中文化界面
- ✅ 中文报告和图表
- ✅ 中文指标名称
- ✅ 中文操作建议
- ✅ 中文错误提示

### 📡 多数据源支持
| 数据源 | 质量 | 限制 | 推荐度 |
|--------|------|------|--------|
| **Tiingo** | ⭐⭐⭐⭐⭐ | 500次/月 | ⭐⭐⭐⭐⭐ |
| **Alpha Vantage** | ⭐⭐⭐⭐ | 5次/分钟 | ⭐⭐⭐⭐ |
| **Yahoo Finance** | ⭐⭐⭐ | 易限流 | ⭐⭐⭐ |
| **Mock** | ⭐⭐ | 无限制 | ⭐⭐ |

### 🎨 A股市场情绪分析
- ✅ **实时Web面板** - 美观的渐变色设计
- ✅ **5大指数追踪** - 上证、深证、创业板、沪深300、中证500
- ✅ **智能评分系统** - -1到+1的情绪评分
- ✅ **操作建议生成** - 根据情绪自动生成建议
- ✅ **历史趋势图** - 情绪变化可视化

---

## 🚀 快速开始

### 安装

```bash
# 克隆项目
cd /Users/user/Desktop/量化ai

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 方式一: Web面板（推荐）

```bash
# 启动Web服务器
./start_web.sh

# 或手动启动
python web_server.py

# 访问地址
http://localhost:5000
```

### 方式二: 命令行回测

```bash
# 使用Tiingo数据（默认，推荐）
python main_chinese.py --symbol AAPL --strategy ma

# 使用Alpha Vantage
python main_chinese.py --symbol AAPL --strategy macd

# 使用模拟数据（测试用）
python main_enhanced.py --sources mock --symbol AAPL

# 中文演示
python run_chinese_demo.py
```

### 方式三: 市场情绪分析

```bash
# 查看市场情绪（命令行）
python market_sentiment_enhanced.py

# 使用模拟数据演示
python market_sentiment_enhanced.py --mock

# 启动Web面板
./start_web.sh
```

---

## 📖 详细使用

### 1. 量化回测

#### 基本回测

```python
from data_fetcher import DataFetcher
from trading_strategies import MovingAverageCrossover
from backtest_engine import BacktestEngine
from chinese_analytics import ChinesePerformanceAnalyzer

# 获取数据（默认使用Tiingo）
fetcher = DataFetcher(source="tiingo")
data = fetcher.fetch_data("AAPL", period="1y")

# 创建策略
strategy = MovingAverageCrossover(short_window=20, long_window=50)

# 运行回测
engine = BacktestEngine(strategy, initial_capital=100000, commission=0.001)
results = engine.run(data, "AAPL")

# 生成中文报告
analyzer = ChinesePerformanceAnalyzer()
report = analyzer.generate_chinese_report(results)
print(report)

# 查看高级指标
equity_curve = results['equity_curve']
advanced = analyzer.calculate_advanced_metrics(equity_curve)
print(f"年化收益率: {advanced['annual_return']:.2%}")
print(f"索提诺比率: {advanced['sortino_ratio']:.2f}")
print(f"卡玛比率: {advanced['calmar_ratio']:.2f}")
```

#### 策略对比

```bash
# 测试不同策略
python main_chinese.py --symbol AAPL --strategy ma       # 移动平均线
python main_chinese.py --symbol AAPL --strategy macd     # MACD
python main_chinese.py --symbol AAPL --strategy rsi      # RSI
python main_chinese.py --symbol AAPL --strategy bollinger # 布林带
```

#### 支持的策略

| 策略 | 代码 | 说明 | 适用场景 |
|------|------|------|----------|
| 移动平均线交叉 | `ma` | 金叉死叉 | 趋势市场 |
| 均值回归 | `mean_reversion` | 价格回归均值 | 震荡市场 |
| 动量策略 | `momentum` | 追涨杀跌 | 强势行情 |
| RSI策略 | `rsi` | 超买超卖 | 震荡/反转 |
| MACD策略 | `macd` | 指标交叉 | 趋势跟踪 |
| 布林带策略 | `bollinger` | 波动通道 | 异常波动 |

### 2. 量化指标（17个）

#### 基础指标（6个）
- **总收益率** - 策略整体收益
- **夏普比率** - 风险调整收益（>1为好）
- **最大回撤** - 最大亏损幅度
- **胜率** - 盈利交易占比
- **盈亏比** - 总盈利/总亏损
- **总交易次数** - 执行的交易笔数

#### 高级指标（11个）

**收益类**:
- 年化收益率 - 折算为年度收益
- 月度收益率 - 平均每月收益

**风险类**:
- 波动率 - 价格波动标准差
- 下行风险 - 负收益的波动
- VaR 95% - 95%置信度下的最大损失
- CVaR 95% - 超过VaR的平均损失

**风险调整收益**:
- 索提诺比率 - 下行风险调整收益
- 卡玛比率 - 回撤调整收益
- 信息比率 - 相对基准的超额收益

**分布特征**:
- 偏度 - 收益分布不对称性
- 峰度 - 分布的尖峰程度

### 3. 市场情绪分析

#### Web面板功能

访问 **http://localhost:5000** 查看：

- 🎯 **综合情绪得分** - -1到+1的可视化评分
- 📈 **5大指数** - 实时价格和涨跌幅
- 🔍 **市场广度** - 涨跌统计、涨跌停数量
- 💡 **操作建议** - 根据情绪自动生成
- 📊 **历史趋势** - 情绪变化折线图

#### 情绪评分说明

| 得分范围 | 情绪状态 | 建议操作 |
|----------|----------|----------|
| ≥ 0.6 | 🚀 强烈看多 | 仓位80-100% |
| 0.3~0.6 | 📈 看多 | 仓位60-70% |
| 0.1~0.3 | ↗️ 偏多 | 仓位30-50% |
| -0.1~0.1 | ➡️ 中性 | 仓位<30% |
| -0.3~-0.1 | ↘️ 偏空 | 仓位<20% |
| -0.6~-0.3 | 📉 看空 | 仓位<10% |
| ≤ -0.6 | 💥 强烈看空 | 完全空仓 |

#### API接口

```bash
# 获取情绪数据
curl http://localhost:5000/api/sentiment

# 强制刷新
curl http://localhost:5000/api/refresh

# 健康检查
curl http://localhost:5000/api/health
```

### 4. Tiingo API使用

#### 获取股票数据

```python
from tiingo_fetcher import TiingoDataFetcher

# 初始化
fetcher = TiingoDataFetcher()

# 获取日线数据
df = fetcher.get_eod_data(
    ticker="AAPL",
    start_date="2025-01-01",
    end_date="2026-01-21",
    frequency="daily"
)
```

#### 获取实时报价

```python
quote = fetcher.get_realtime_quote("AAPL")
print(f"最新价: {quote['last']}")
print(f"买价: {quote['bid']}")
print(f"卖价: {quote['ask']}")
```

#### 加密货币数据

```python
crypto_df = fetcher.get_crypto_data("btcusd")
```

**API密钥**: `ef36156b72b04df949358dd625686d9e2ba728f6`

---

## 📁 项目结构

```
量化ai/
├── 📄 README.md                      # 本文档
├── 📄 requirements.txt               # Python依赖
├── 📄 config.yaml                    # 配置文件
│
├── 🐍 核心模块
│   ├── data_fetcher.py              # 数据获取（Tiingo/AV/Yahoo）
│   ├── tiingo_fetcher.py            # Tiingo API ⭐
│   ├── technical_indicators.py      # 15+技术指标
│   ├── trading_strategies.py        # 6种交易策略
│   ├── backtest_engine.py           # 回测引擎
│   ├── risk_management.py           # 风险管理
│   └── performance_analytics.py     # 性能分析
│
├── 🌏 中文版
│   ├── chinese_analytics.py         # 中文性能分析 ⭐
│   ├── chinese_ui_config.py         # 中文UI配置
│   ├── main_chinese.py              # 中文主程序 ⭐
│   └── run_chinese_demo.py          # 中文演示
│
├── 📊 市场情绪分析
│   ├── market_sentiment_enhanced.py # 情绪分析引擎 ⭐
│   ├── web_server.py                # Flask服务器 ⭐
│   ├── start_web.sh                 # 启动脚本
│   └── templates/
│       └── sentiment_dashboard.html # Web面板
│
├── 📚 文档
│   ├── 使用指南.md                  # 系统使用指南
│   ├── TIINGO_API_GUIDE.md          # Tiingo指南
│   ├── WEB_DASHBOARD_GUIDE.md       # Web面板指南
│   ├── FINAL_GUIDE.md               # 最终指南
│   ├── PROJECT_STATUS.md            # 项目状态
│   └── CHINESE_VERSION_SUMMARY.md   # 中文版总结
│
├── 📂 data/                         # 数据存储
├── 📂 results/                      # 回测结果
│   ├── *.csv                       # CSV数据
│   ├── *.html                      # HTML报告
│   └── *.png                       # 图表文件
└── 📂 logs/                         # 日志文件
```

---

## 🎨 可视化报告

### 1. HTML报告
- ✅ 完全中文界面
- ✅ 渐变色彩设计
- ✅ 响应式布局
- ✅ 动态徽章评价
- ✅ 所有指标展示

### 2. 图表展示
- ✅ 账户净值曲线
- ✅ 回撤曲线
- ✅ 日收益率分布
- ✅ 累计收益率
- ✅ 收益率箱线图
- ✅ 滚动夏普比率

### 3. 数据导出
- ✅ CSV格式 - 表格软件查看
- ✅ HTML格式 - 浏览器查看
- ✅ PNG格式 - 图片查看

---

## ⚙️ 配置说明

### config.yaml

```yaml
# 数据配置
data:
  source: "tiingo"              # 数据源: tiingo, alpha_vantage, yahoo
  api_key: "your_api_key"       # API密钥
  symbols: ["AAPL", "MSFT"]     # 股票代码
  interval: "1d"                # 数据间隔
  period: "2y"                  # 时间周期

# 策略配置
strategy:
  name: "ma"                    # 策略名称
  parameters:
    short_window: 20
    long_window: 50

# 回测配置
backtest:
  initial_capital: 100000       # 初始资金
  commission: 0.001             # 手续费率
  slippage: 0.0001              # 滑点

# 风险管理
risk:
  max_position_size: 0.2        # 单个标的最大仓位
  max_total_position: 0.8       # 总仓位限制
  max_drawdown: 0.15            # 最大回撤限制
```

---

## 🔧 高级功能

### 1. 自定义策略

```python
from trading_strategies import BaseStrategy

class MyStrategy(BaseStrategy):
    def __init__(self, param1=10, param2=20):
        super().__init__()
        self.param1 = param1
        self.param2 = param2
        self.parameters = {'param1': param1, 'param2': param2}

    def generate_signals(self, data):
        # 实现你的策略逻辑
        data['signal'] = 0
        # ... 代码 ...
        return data
```

### 2. 自定义指标

```python
from technical_indicators import TechnicalIndicators

@staticmethod
def my_indicator(data, window=20):
    # 实现指标计算
    return result
```

### 3. 批量回测

```python
symbols = ["AAPL", "MSFT", "GOOGL", "TSLA"]
results = {}

for symbol in symbols:
    data = fetcher.fetch_data(symbol, period="1y")
    result = engine.run(data, symbol)
    results[symbol] = result
```

---

## 📊 性能指标详解

### 收益类指标
- **总收益率**: `(最终价值 - 初始资金) / 初始资金`
- **年化收益率**: `(1 + 总收益率)^(1/年数) - 1`

### 风险类指标
- **最大回撤**: 从峰值到谷值的最大跌幅
- **波动率**: 日收益率标准差 × √252
- **下行风险**: 负收益率标准差 × √252
- **VaR 95%**: 第5百分位的收益率
- **CVaR 95%**: 超过VaR的平均损失

### 风险调整收益
- **夏普比率**: `(收益率 - 无风险利率) / 波动率`
- **索提诺比率**: `(收益率 - 无风险利率) / 下行风险`
- **卡玛比率**: `年化收益率 / |最大回撤|`

---

## ⚠️ 重要提示

1. **历史表现不代表未来** - 回测结果不能保证实际收益
2. **避免过拟合** - 不要过度优化参数
3. **考虑交易成本** - 实际交易可能有额外费用
4. **风险控制** - 始终使用止损和仓位管理
5. **市场变化** - 策略有效性可能随时间变化
6. **API限制** - 注意各数据源的调用限制

---

## 🛠️ 故障排除

### 问题1: API调用失败
```
❌ 获取数据失败: HTTP 403
```
**解决**: 检查API密钥，或切换数据源

### 问题2: 端口被占用
```
Address already in use
Port 5000 is in use
```
**解决**: 系统会自动尝试其他端口（8080, 3000）

### 问题3: 导入错误
```
ModuleNotFoundError: No module named 'xxx'
```
**解决**:
```bash
pip install -r requirements.txt
```

### 问题4: Web服务器无法启动
**解决**:
```bash
# 检查Flask是否安装
pip install flask

# 检查端口占用
lsof -i:5000
```

---

## 📚 相关文档

- [使用指南.md](使用指南.md) - 详细使用说明
- [TIINGO_API_GUIDE.md](TIINGO_API_GUIDE.md) - Tiingo API指南
- [WEB_DASHBOARD_GUIDE.md](WEB_DASHBOARD_GUIDE.md) - Web面板指南
- [FINAL_GUIDE.md](FINAL_GUIDE.md) - 最终完整指南
- [PROJECT_STATUS.md](PROJECT_STATUS.md) - 项目当前状态

---

## 🤝 贡献

欢迎提交问题和拉取请求！

---

## 📄 许可证

MIT License - 自由使用和修改

---

## 🎯 适用场景

✅ 量化交易策略开发
✅ 技术指标研究
✅ 风险管理测试
✅ 投资组合优化
✅ 算法交易学习
✅ 金融数据分析
✅ 市场情绪监控
✅ A股市场分析

---

## 💡 技术栈

- **Python 3.7+** - 核心语言
- **pandas** - 数据处理
- **numpy** - 数值计算
- **matplotlib** - 数据可视化
- **Flask** - Web服务器
- **Chart.js** - 前端图表
- **Tiingo API** - 数据源 ⭐
- **Alpha Vantage** - 数据源
- **Yahoo Finance** - 数据源

---

## 📞 联系方式

如有问题或建议，欢迎提交Issue。

---

## 🎉 总结

您现在拥有一个**完整的量化交易系统**！

✅ **完整回测** - 6种策略 + 17个指标
✅ **中文界面** - 完全中文化
✅ **市场分析** - 实时情绪面板
✅ **多数据源** - Tiingo/AV/Yahoo
✅ **风险管理** - 完整风控模块
✅ **专业报告** - HTML/CSV/图表

**开始您的量化交易之旅！** 📈💰✨

---

**最后更新**: 2026年1月21日
**版本**: v3.0
**状态**: ✅ 生产就绪
