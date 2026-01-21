# 🎯 量化交易系统 - 使用指南

## ✅ 系统已就绪!

您的量化交易系统已经完全配置好,可以随时使用!

## 🚀 立即开始

### 方式1: 增强版主程序 (推荐⭐)

```bash
# 激活虚拟环境
source venv/bin/activate

# 使用模拟数据 (最快,最稳定)
python main_enhanced.py --symbol AAPL --sources mock

# 尝试真实数据 (自动切换到mock如果失败)
python main_enhanced.py --symbol AAPL

# 多策略对比
python main_enhanced.py --compare --symbol AAPL --sources mock
```

### 方式2: 离线版主程序

```bash
# 完全离线
python main_offline.py --symbol AAPL
python main_offline.py --compare --symbol AAPL
```

## 📊 可用命令

```bash
# 单个股票回测
python main_enhanced.py --symbol AAPL

# 指定策略
python main_enhanced.py --symbol AAPL --strategy macd

# 指定时间范围
python main_enhanced.py --symbol AAPL --period 1y

# 多个数据源
python main_enhanced.py --symbol AAPL --sources yahoo mock stooq

# 查看帮助
python main_enhanced.py --help
```

## 📈 可用策略

1. `moving_average_crossover` - 移动平均线交叉
2. `mean_reversion` - 均值回归
3. `momentum` - 动量策略
4. `rsi` - RSI策略
5. `macd` - MACD策略
6. `bollinger_bands` - 布林带策略

## 📁 查看结果

```bash
# 在浏览器中打开HTML报告
open results/AAPL_*.html

# 查看图表
open results/AAPL_*_equity_*.png
open results/AAPL_*_trades_*.png
```

## 🔧 解决API限流

如果遇到API限流问题:

```bash
# 方案1: 使用mock数据
python main_enhanced.py --sources mock --symbol AAPL

# 方案2: 使用离线版
python main_offline.py --symbol AAPL

# 方案3: 查看详细解决方案
cat API_SOLUTION.md
```

## 📚 更多文档

- [START_HERE.md](START_HERE.md) - 快速开始
- [API_SOLUTION.md](API_SOLUTION.md) - API解决方案
- [README.md](README.md) - 完整文档
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - 项目总结

## 💡 常见问题

**Q: 如何避免API限流?**
A: 使用 `--sources mock` 参数,或使用 `main_offline.py`

**Q: 如何使用真实数据?**
A: 运行 `python main_enhanced.py --symbol AAPL`,会自动尝试Yahoo Finance

**Q: 数据从哪来?**
A:
- Yahoo Finance (真实,有限制)
- Mock数据 (模拟,无限制)
- Stooq (真实,免费)

**Q: 可以回测哪些股票?**
A: 任何美股代码,如: AAPL, MSFT, GOOGL, TSLA, NVDA等

## 🎓 学习路径

1. **初学者**: 使用mock数据学习系统
   ```bash
   python main_enhanced.py --sources mock --symbol AAPL
   ```

2. **进阶者**: 尝试真实数据,对比策略
   ```bash
   python main_enhanced.py --compare --symbol AAPL --sources yahoo mock
   ```

3. **研究者**: 优化参数,开发策略
   - 编辑 config.yaml
   - 创建自定义策略
   - 分析回测结果

## 🎉 开始探索

```bash
source venv/bin/activate
python main_enhanced.py --symbol AAPL --sources mock
```

祝您交易愉快! 📈💰
