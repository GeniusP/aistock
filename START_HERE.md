# ⚡ 30秒快速开始

## 一、安装 (选择一种方式)

### 🌟 推荐: 使用一键安装脚本

```bash
cd /Users/user/Desktop/量化ai
./setup.sh
```

### 📝 或手动安装

```bash
cd /Users/user/Desktop/量化ai
python3 -m venv venv
source venv/bin/activate
pip install pandas numpy yfinance matplotlib seaborn scipy scikit-learn
```

## 二、运行测试

```bash
# 确保虚拟环境已激活
source venv/bin/activate

# 测试系统
python test_system.py
```

## 三、开始使用

### 选项1: 命令行方式 (最简单)

```bash
# 回测AAPL股票
python main.py --symbol AAPL

# 对比多个策略
python main.py --compare --symbol AAPL

# 查看帮助
python main.py --help
```

### 选项2: 运行示例

```bash
python example.py
```

### 选项3: Python代码

```python
from data_fetcher import DataFetcher
from trading_strategies import MovingAverageCrossover
from backtest_engine import BacktestEngine

# 获取数据
fetcher = DataFetcher()
data = fetcher.fetch_data("AAPL", period="1y")

# 创建策略
strategy = MovingAverageCrossover(20, 50)

# 运行回测
engine = BacktestEngine(strategy, initial_capital=100000)
results = engine.run(data, "AAPL")

# 查看结果
print(f"收益率: {results['total_return']:.2%}")
print(f"夏普比率: {results['sharpe_ratio']:.2f}")
```

## 📊 查看结果

回测完成后,结果保存在 `results/` 目录:

```bash
# 查看HTML报告
open results/AAPL_report_*.html

# 查看图表
open results/*.png
```

## 🎯 可用策略

- `moving_average_crossover` - 移动平均线交叉
- `mean_reversion` - 均值回归
- `momentum` - 动量策略
- `rsi` - RSI策略
- `macd` - MACD策略
- `bollinger_bands` - 布林带

## 💡 使用示例

```bash
# 使用特定策略
python main.py --symbol AAPL --strategy macd

# 回测多只股票
python main.py --symbols AAPL MSFT GOOGL

# 修改配置文件后使用
# 编辑 config.yaml,然后运行:
python main.py
```

## 📚 更多信息

- 📖 [完整文档](README.md)
- 🚀 [详细指南](QUICKSTART.md)
- 🖥️ [Mac安装说明](INSTALL_MAC.md)
- 📊 [项目总结](PROJECT_SUMMARY.md)

## ⚠️ 注意事项

1. 每次使用前先激活虚拟环境: `source venv/bin/activate`
2. 数据需要网络连接,可能需要VPN访问Yahoo Finance
3. 历史回测不代表未来收益

## 🎉 开始您的量化交易之旅!

```bash
./setup.sh && source venv/bin/activate && python main.py --symbol AAPL
```

一行命令,完成安装到回测! 📈
