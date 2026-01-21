#!/usr/bin/env python3
"""
完全中文化的量化交易系统
所有界面和报告都是中文
"""

import sys
sys.path.insert(0, '/Users/user/Desktop/量化ai')

import pandas as pd
import numpy as np
from datetime import datetime

# 设置中文字体
from chinese_ui_config import set_chinese_style, ChineseUI

set_chinese_style()

print("""
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║              📊 量化交易回测系统 - 完全中文版 v3.0                      ║
║                                                                   ║
║              所有界面和报告都是中文,易于理解和使用                         ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
""")

print("\n📋 系统功能:")
print("  1. 一键回测     - 自动执行完整回测流程")
print("  2. 智能分析     - 计算所有量化指标")
print("  3. 图表生成     - 创建专业可视化报告")
print("  4. 数据导出     - 支持CSV和HTML格式")

print("\n💡 立即开始:")
print("  python main_enhanced.py --sources mock --symbol AAPL")
print("  python run_chinese_demo.py")

print("\n" + "="*80)

# 显示中文术语对照表
print("\n📖 英文-中文术语对照表:")
print("-" * 80)

terms = [
    ("Open", "开盘价"),
    ("High", "最高价"),
    ("Low", "最低价"),
    ("Close", "收盘价"),
    ("Volume", "成交量"),
    ("Buy", "买入"),
    ("Sell", "卖出"),
    ("Long", "做多"),
    ("Short", "做空"),
    ("Sharpe Ratio", "夏普比率"),
    ("Max Drawdown", "最大回撤"),
    ("Volatility", "波动率"),
    ("Win Rate", "胜率"),
    ("Profit Factor", "盈亏比"),
    ("Moving Average", "移动平均线"),
    ("RSI", "相对强弱指标"),
    ("MACD", "指数平滑异同移动平均线"),
    ("Bollinger Bands", "布林带"),
]

for en, cn in terms:
    print(f"  {en:20s} → {cn}")

print("\n" + "="*80)
print("✅ 中文化完成!")
print("="*80)

print("\n🎯 您的系统现在完全支持:")
print("  ✓ 中文菜单和提示")
print("  ✓ 中文指标名称")
print("  ✓ 中文报告和图表")
print("  ✓ 中文错误信息")

print("\n🚀 立即体验:")
print("  python main_enhanced.py --sources mock --symbol AAPL")
print("  python run_chinese_demo.py")

print("\n📚 查看完整文档:")
print("  cat FINAL_GUIDE.md")
print("  open FINAL_GUIDE.md")

print("\n" + "="*80)
print("系统已完全中文化! 🎉")
print("="*80)
