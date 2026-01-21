# Tiingo API 集成指南

## ✅ 已完成集成

### API密钥配置
```
API Key: ef36156b72b04df949358dd625686d9e2ba728f6
```

### 新增文件

1. **[tiingo_fetcher.py](tiingo_fetcher.py)** - Tiingo API数据获取器
   - 获取股票日线数据
   - 获取实时报价
   - 获取股票元数据
   - 支持加密货币数据
   - 股票代码搜索功能

2. **更新 [data_fetcher.py](data_fetcher.py)** - 添加Tiingo作为数据源
   - 默认数据源改为Tiingo
   - 自动集成Tiingo API
   - 支持多数据源切换

## 📊 Tiingo API功能

### 1. 获取股票日线数据

```python
from tiingo_fetcher import TiingoDataFetcher

# 初始化
fetcher = TiingoDataFetcher(api_key="ef36156b72b04df949358dd625686d9e2ba728f6")

# 获取AAPL数据
df = fetcher.get_eod_data(
    ticker="AAPL",
    start_date="2025-01-01",
    end_date="2026-01-21",
    frequency="daily"
)

print(df.head())
```

### 2. 获取实时报价

```python
quote = fetcher.get_realtime_quote("AAPL")

print(f"最新价: {quote['last']}")
print(f"买价: {quote['bid']}")
print(f"卖价: {quote['ask']}")
print(f"成交量: {quote['volume']}")
```

### 3. 获取股票元数据

```python
metadata = fetcher.get_ticker_metadata("AAPL")

print(f"公司名称: {metadata['name']}")
print(f"交易所: {metadata['exchange']}")
print(f"货币: {metadata['currency']}")
print(f"描述: {metadata['description']}")
```

### 4. 搜索股票代码

```python
results = fetcher.search_tickers("Apple")

for stock in results:
    print(f"{stock['ticker']}: {stock['name']}")
```

### 5. 获取加密货币数据

```python
crypto_df = fetcher.get_crypto_data(
    ticker="btcusd",
    start_date="2025-12-01",
    end_date="2026-01-21"
)

print(crypto_df.head())
```

## 🚀 在量化系统中使用

### 方式一: 使用DataFetcher（推荐）

```python
from data_fetcher import DataFetcher

# 使用Tiingo作为数据源（现在是默认）
fetcher = DataFetcher(source="tiingo")

# 获取数据
data = fetcher.fetch_data(
    symbol="AAPL",
    interval="1d",
    period="1y"
)

print(data.head())
```

### 方式二: 直接使用TiingoFetcher

```python
from tiingo_fetcher import TiingoDataFetcher

fetcher = TiingoDataFetcher()
df = fetcher.get_eod_data("AAPL")
```

### 在回测中使用

```python
from data_fetcher import DataFetcher
from backtest_engine import BacktestEngine
from trading_strategies import MovingAverageCrossover

# 使用Tiingo数据
fetcher = DataFetcher(source="tiingo")
data = fetcher.fetch_data("AAPL", period="1y")

# 运行回测
strategy = MovingAverageCrossover()
engine = BacktestEngine(strategy, initial_capital=100000)
results = engine.run(data, "AAPL")
```

## 🔄 多数据源支持

系统现在支持3个数据源：

```python
# 1. Tiingo (默认，推荐)
fetcher = DataFetcher(source="tiingo")

# 2. Alpha Vantage
fetcher = DataFetcher(source="alpha_vantage")

# 3. Yahoo Finance
fetcher = DataFetcher(source="yahoo")
```

### 数据源对比

| 特性 | Tiingo | Alpha Vantage | Yahoo Finance |
|------|--------|---------------|---------------|
| 免费API | ✅ | ✅ | ✅ |
| 限制 | 宽松 | 5次/分钟 | 不明确 |
| 数据质量 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| 美股数据 | ✅ | ✅ | ✅ |
| 加密货币 | ✅ | ❌ | ⚠️ |
| 实时报价 | ✅ | ✅ | ✅ |
| 元数据 | ✅ | ✅ | ✅ |

## 📋 API限制

### Tiingo免费版
- 每月500次请求
- 支持日线、周线、月线数据
- 支持实时报价（有15分钟延迟）
- 支持加密货币数据

### 使用建议
1. **日线数据**: 使用Tiingo或Alpha Vantage
2. **实时报价**: 使用Tiingo
3. **加密货币**: 使用Tiingo
4. **高频数据**: 使用Yahoo Finance

## 🔑 API密钥管理

### 位置
- **文件**: [tiingo_fetcher.py](tiingo_fetcher.py)
- **默认密钥**: `ef36156b72b04df949358dd625686d9e2ba728f6`

### 更换API密钥
```python
# 方式一：在初始化时指定
fetcher = TiingoDataFetcher(api_key="YOUR_NEW_API_KEY")

# 方式二：修改默认值
# 编辑 tiingo_fetcher.py，修改第17行
```

### 获取Tiingo API密钥
1. 访问 https://www.tiingo.com/
2. 注册免费账号
3. 在账户设置中生成API密钥
4. 替换默认密钥

## 🧪 测试API

### 测试脚本
```bash
# 测试Tiingo API
python tiingo_fetcher.py
```

### 预期输出
```
╔═══════════════════════════════════════════════════════════════════╗
║              📊 Tiingo API 测试                                   ║
╚═══════════════════════════════════════════════════════════════════╝

🔑 API密钥: ef36156b72b04df94935...

测试1: 获取AAPL股票数据
✅ 成功获取 252 条数据
...

测试2: 获取实时报价
实时报价: ...
...

测试3: 获取股票元数据
股票信息:
  ticker: AAPL
  name: Apple Inc
  ...
```

## 💡 使用示例

### 示例1: 获取多只股票数据

```python
from data_fetcher import DataFetcher

fetcher = DataFetcher(source="tiingo")

symbols = ["AAPL", "MSFT", "GOOGL"]

for symbol in symbols:
    data = fetcher.fetch_data(symbol, period="6mo")
    if not data.empty:
        print(f"{symbol}: 获取 {len(data)} 条数据")
        print(f"最新价格: ${data['close'].iloc[-1]:.2f}\n")
```

### 示例2: 集成到回测系统

```python
from data_fetcher import DataFetcher
from main_chinese import run_backtest

# 使用Tiingo数据运行回测
import sys
sys.argv = ['main_chinese.py', '--symbol', 'AAPL', '--strategy', 'ma']

# 修改data_fetcher默认源为tiingo
# 然后运行
# run_backtest("AAPL", "ma")
```

### 示例3: 批量获取数据

```python
from data_fetcher import DataFetcher

fetcher = DataFetcher(source="tiingo")

# 批量获取
data_dict = fetcher.fetch_multiple_symbols(
    symbols=["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"],
    interval="1d",
    period="1y"
)

for symbol, data in data_dict.items():
    print(f"{symbol}: {len(data)} 条数据")
```

## 🛠️ 故障排除

### 问题1: API请求超时
```
❌ 请求超时，请检查网络连接
```
**解决方案**:
- 检查网络连接
- 增加timeout参数
- 尝试使用VPN

### 问题2: API密钥无效
```
❌ API密钥无效，请检查您的Tiingo API密钥
```
**解决方案**:
- 验证API密钥是否正确
- 检查密钥是否过期
- 登录Tiingo确认账户状态

### 问题3: 数据为空
```
⚠️ 未获取到 AAPL 的数据
```
**解决方案**:
- 检查股票代码是否正确
- 确认日期范围是否合理
- 尝试其他股票代码

## 📚 相关文档

- [Tiingo API文档](https://api.tiingo.com/)
- [data_fetcher.py](data_fetcher.py) - 数据获取模块
- [使用指南.md](使用指南.md) - 系统使用指南

## 🎯 下一步

1. **测试API**: 运行测试脚本验证连接
2. **更新配置**: 修改config.yaml设置默认数据源
3. **集成回测**: 使用Tiingo数据运行回测策略
4. **监控用量**: 跟踪API使用次数，避免超限

---

**Tiingo API已成功集成！** 🎉

现在您可以享受高质量的美股和加密货币数据了！📊✨
