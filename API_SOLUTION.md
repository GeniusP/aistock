# 🔄 API限流解决方案

## 问题说明

Yahoo Finance API 有访问频率限制,可能导致以下错误:
```
Too Many Requests. Rate limited. Try after a while.
```

## ✅ 解决方案

我们提供了**增强版数据获取器**,支持多个数据源自动切换!

### 📡 可用数据源

| 数据源 | 说明 | 需要 | 限制 |
|--------|------|------|------|
| **yahoo** | Yahoo Finance | 无 | 有限制,可能需要VPN |
| **mock** | 模拟数据 | 无 | 无限制,数据为模拟 |
| **stooq** | Stooq | 无 | 免费但数据较旧 |
| **polygon** | Polygon.io | API Key | 需免费注册 |

## 🚀 使用方法

### 方式1: 使用增强版主程序 (推荐)

```bash
# 激活环境
source venv/bin/activate

# 自动切换数据源 (yahoo优先,失败则用mock)
python main_enhanced.py --symbol AAPL

# 强制使用模拟数据
python main_enhanced.py --symbol AAPL --sources mock

# 指定多个数据源(按优先级)
python main_enhanced.py --symbol AAPL --sources yahoo stooq mock

# 使用特定策略
python main_enhanced.py --symbol AAPL --strategy macd --sources mock

# 多策略对比
python main_enhanced.py --compare --symbol AAPL --sources mock
```

### 方式2: 代码中使用

```python
from data_fetcher_enhanced import EnhancedDataFetcher

# 创建数据获取器,指定数据源
fetcher = EnhancedDataFetcher(sources=['yahoo', 'mock'])

# 获取数据(自动在数据源间切换)
data = fetcher.fetch_data("AAPL", period="2y")

# 检查数据来源
if not data.empty:
    print(f"获取到 {len(data)} 条数据")
```

### 方式3: 使用离线版主程序

```bash
# 完全离线,使用模拟数据
python main_offline.py --symbol AAPL
python main_offline.py --compare --symbol AAPL
```

## 💡 推荐配置

### 对于学习测试

使用模拟数据,快速稳定:

```bash
python main_enhanced.py --symbol AAPL --sources mock
```

### 对于实盘研究

尝试多个数据源,获取真实数据:

```bash
# 先尝试yahoo,如果失败则用stooq
python main_enhanced.py --symbol AAPL --sources yahoo stooq mock

# 或使用Polygon (需要API key)
# 1. 访问 https://polygon.io/ 免费注册
# 2. 获取API key
# 3. 修改 data_fetcher_enhanced.py 中的 API_KEY
```

## 🔧 高级配置

### 添加Polygon.io支持

1. 访问 https://polygon.io/ 免费注册
2. 获取API Key
3. 编辑 [data_fetcher_enhanced.py](data_fetcher_enhanced.py)

```python
def _fetch_polygon(self, symbol: str, interval: str, period: str):
    api_key = "YOUR_ACTUAL_API_KEY"  # 替换这里
    # ... 其余代码
```

### 调整请求延迟

编辑 [data_fetcher_enhanced.py](data_fetcher_enhanced.py):

```python
def fetch_multiple_symbols(self, symbols, ...):
    # 增加延迟避免限流
    delay: float = 1.0  # 从0.5改为1秒
```

## 📊 数据质量对比

| 数据源 | 真实性 | 时效性 | 稳定性 | 推荐用途 |
|--------|--------|--------|--------|----------|
| Yahoo | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 实盘研究 |
| Mock | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 学习测试 |
| Stooq | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | 历史数据 |
| Polygon | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 专业使用 |

## 🎯 最佳实践

### 1. 开发阶段

```bash
# 使用mock数据,快速迭代
python main_enhanced.py --sources mock --symbol AAPL
```

### 2. 测试阶段

```bash
# 尝试获取真实数据
python main_enhanced.py --sources yahoo stooq mock --symbol AAPL
```

### 3. 生产阶段

```bash
# 使用多个数据源确保可用性
python main_enhanced.py --sources yahoo polygon stooq mock --symbol AAPL
```

## ⚠️ 注意事项

1. **数据质量**: Mock数据仅供学习,实盘需用真实数据
2. **API限制**: Yahoo限制较严,建议配合其他数据源
3. **网络问题**: 如遇限流,等待后重试或使用VPN
4. **缓存机制**: 增强版会缓存数据,避免重复请求

## 🔍 故障排查

### 问题1: Yahoo API持续限流

```bash
# 解决方案1: 只用mock数据
python main_enhanced.py --sources mock --symbol AAPL

# 解决方案2: 增加延迟
# 编辑 data_fetcher_enhanced.py,增加重试延迟

# 解决方案3: 使用VPN
```

### 问题2: 所有数据源都失败

```bash
# 检查网络连接
ping google.com

# 使用离线模式
python main_offline.py --symbol AAPL
```

### 问题3: 数据不连续

```bash
# mock数据是连续的
python main_enhanced.py --sources mock --symbol AAPL

# 真实数据可能有节假日,是正常的
```

## 📚 相关文件

- [data_fetcher_enhanced.py](data_fetcher_enhanced.py) - 增强版数据获取器
- [main_enhanced.py](main_enhanced.py) - 增强版主程序
- [main_offline.py](main_offline.py) - 离线版主程序
- [data_fetcher.py](data_fetcher.py) - 原始数据获取器

## 🎉 总结

现在您有**3种方式**避免API限流:

1. ✅ **增强版** - 多数据源自动切换
2. ✅ **离线版** - 完全使用模拟数据
3. ✅ **配置版** - 调整延迟和重试

选择最适合您的方式!

---

**Happy Trading! 📈💰**
