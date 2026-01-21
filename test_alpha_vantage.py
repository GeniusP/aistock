#!/usr/bin/env python3
"""
测试Alpha Vantage API连接
"""

import sys
sys.path.insert(0, '/Users/user/Desktop/量化ai')

from data_fetcher import DataFetcher

print("=" * 80)
print("测试 Alpha Vantage API")
print("=" * 80)

# 创建数据获取器,使用Alpha Vantage
api_key = "RQMP1U6N9J2OMIWH"
fetcher = DataFetcher(source="alpha_vantage", api_key=api_key)

print(f"\n📡 使用API Key: {api_key[:10]}...")
print(f"📊 数据源: Alpha Vantage")
print(f"⏳ 请耐心等待,API有请求频率限制...")

# 测试获取AAPL数据
print(f"\n正在获取 AAPL 数据...")
data = fetcher.fetch_data("AAPL", interval="1d", period="6mo")

if not data.empty:
    print(f"\n✅ 成功获取数据!")
    print(f"   数据行数: {len(data)}")
    print(f"   日期范围: {data['datetime'].min()} 到 {data['datetime'].max()}")
    print(f"   列名: {data.columns.tolist()}")
    print(f"\n最近5天数据:")
    print(data.tail()[['datetime', 'open', 'high', 'low', 'close', 'volume']])

    # 保存数据
    fetcher.save_data(data, "AAPL", "1d")
    print(f"\n💾 数据已保存")

else:
    print("\n❌ 获取数据失败")
    print("\n可能的原因:")
    print("  • API Key无效")
    print("  • API调用频率超限 (免费版: 每分钟5次)")
    print("  • 网络连接问题")
    print("  • 股票代码不存在")

print("\n" + "=" * 80)
print("测试完成")
print("=" * 80)

print("\n💡 使用说明:")
print("  • Alpha Vantage免费版限制:")
print("    - 每分钟5次请求")
print("    - 每天25次请求")
print("    - 每月500次请求")
print("  • 系统已自动添加12秒延迟")
print("  • 建议批量获取时增加间隔")
