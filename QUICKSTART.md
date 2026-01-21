# 快速开始指南

## 1. 安装

### 基础安装

```bash
# 克隆或下载项目
cd 量化ai

# 安装Python依赖
pip install -r requirements.txt
```

### TA-Lib安装 (可选但推荐)

TA-Lib需要额外安装:

**macOS:**
```bash
brew install ta-lib
pip install ta-lib
```

**Linux:**
```bash
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
pip install ta-lib
```

**Windows:**
下载预编译的wheel文件: https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib

## 2. 测试系统

运行测试脚本验证安装:

```bash
python test_system.py
```

你应该看到所有测试通过。

## 3. 快速示例

### 方式1: 使用主程序

```bash
# 使用默认配置回测AAPL
python main.py --symbol AAPL

# 回测多个股票
python main.py --symbols AAPL MSFT GOOGL

# 使用特定策略
python main.py --symbol AAPL --strategy macd

# 对比多个策略
python main.py --compare --symbol AAPL
```

### 方式2: 运行示例脚本

```bash
python example.py
```

### 方式3: Python代码

```python
from data_fetcher import DataFetcher
from trading_strategies import MovingAverageCrossover
from backtest_engine import BacktestEngine

# 获取数据
fetcher = DataFetcher()
data = fetcher.fetch_data("AAPL", period="2y")

# 创建策略
strategy = MovingAverageCrossover(20, 50)

# 运行回测
engine = BacktestEngine(strategy, initial_capital=100000)
results = engine.run(data, "AAPL")

# 查看结果
print(f"收益率: {results['total_return']:.2%}")
print(f"夏普比率: {results['sharpe_ratio']:.2f}")
```

## 4. 配置文件

编辑 `config.yaml` 自定义参数:

```yaml
data:
  symbols: ["AAPL", "MSFT"]  # 修改为你要测试的股票
  period: "2y"               # 数据时间范围

strategy:
  name: "moving_average_crossover"  # 选择策略
  parameters:
    short_window: 20
    long_window: 50

backtest:
  initial_capital: 100000   # 初始资金
```

## 5. 查看结果

回测完成后,结果保存在 `results/` 目录:
- `*_equity.png` - 权益曲线图
- `*_trades.png` - 交易分析图
- `*_report.html` - HTML格式报告
- `*_trades.csv` - 交易记录CSV
- `*_equity.csv` - 权益曲线CSV

## 6. 策略列表

可用策略:
- `moving_average_crossover` - 移动平均线交叉
- `mean_reversion` - 均值回归
- `momentum` - 动量策略
- `rsi` - RSI策略
- `macd` - MACD策略
- `bollinger_bands` - 布林带

## 7. 常见问题

**Q: 数据获取失败?**
A: 检查网络连接,某些数据可能需要VPN访问

**Q: TA-Lib安装失败?**
A: 可以先不安装TA-Lib,系统仍可运行(部分功能受限)

**Q: 如何添加自己的策略?**
A: 参考 `trading_strategies.py`,继承 `BaseStrategy` 类

**Q: 回测很慢?**
A: 减少数据时间范围或选择较少的交易标的

## 8. 下一步

- 阅读 [README.md](README.md) 了解更多功能
- 查看 [example.py](example.py) 学习更多用法
- 修改 `config.yaml` 实验不同参数
- 创建自己的策略并回测

## 9. 项目结构

```
量化ai/
├── main.py                   # 主程序
├── example.py                # 示例脚本
├── test_system.py            # 测试脚本
├── config.yaml               # 配置文件
├── data_fetcher.py           # 数据获取
├── technical_indicators.py   # 技术指标
├── trading_strategies.py     # 交易策略
├── backtest_engine.py        # 回测引擎
├── risk_management.py        # 风险管理
├── performance_analytics.py  # 性能分析
├── data/                     # 数据目录
├── results/                  # 结果目录
└── logs/                     # 日志目录
```

祝你交易愉快! 📈
