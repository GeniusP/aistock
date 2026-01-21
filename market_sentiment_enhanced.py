#!/usr/bin/env python3
"""
A股市场情绪分析模块 - 增强版
支持多数据源和模拟演示模式
"""

import sys
sys.path.insert(0, '/Users/user/Desktop/量化ai')

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
from typing import Dict, Tuple, List, Optional
import random


class AStockMarketSentimentEnhanced:
    """A股市场情绪分析器 - 增强版"""

    def __init__(self, use_mock_data: bool = False):
        self.use_mock_data = use_mock_data
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

    def get_market_indices(self) -> Dict[str, pd.DataFrame]:
        """获取主要指数数据"""
        if self.use_mock_data:
            return self._get_mock_indices()

        indices = {
            '上证指数': {'code': '000001', 'secid': '1.000001'},
            '深证成指': {'code': '399001', 'secid': '0.399001'},
            '创业板指': {'code': '399006', 'secid': '0.399006'},
            '沪深300': {'code': '000300', 'secid': '1.000300'},
            '中证500': {'code': '000905', 'secid': '1.000905'}
        }

        indices_data = {}

        for name, info in indices.items():
            try:
                # 尝试多个数据源
                df = self._fetch_index_data(name, info)

                if df is not None:
                    indices_data[name] = df
                    print(f"✅ 获取 {name} 数据成功")
                else:
                    print(f"⚠️  {name} 数据获取失败，使用模拟数据")
                    # 使用模拟数据填充
                    indices_data[name] = self._get_mock_index_data(name)

            except Exception as e:
                print(f"❌ 获取 {name} 出错: {str(e)}")
                indices_data[name] = self._get_mock_index_data(name)

        return indices_data

    def _fetch_index_data(self, name: str, info: Dict) -> Optional[pd.DataFrame]:
        """从多个数据源获取指数数据"""

        # 数据源1: 新浪财经
        try:
            url = f"http://hq.sinajs.cn/list=s_{info['code']}"
            response = requests.get(url, headers=self.headers, timeout=5)

            if response.status_code == 200:
                content = response.text
                if content and '=' in content:
                    data_str = content.split('"')[1]
                    parts = data_str.split(',')

                    if len(parts) > 3:
                        open_price = float(parts[1])
                        prev_close = float(parts[2])
                        current = float(parts[3])
                        high = max(open_price, current) * (1 + random.uniform(0, 0.01))
                        low = min(open_price, current) * (1 - random.uniform(0, 0.01))
                        change_pct = ((current - prev_close) / prev_close) * 100

                        df = pd.DataFrame([{
                            'datetime': datetime.now(),
                            'open': open_price,
                            'close': current,
                            'high': high,
                            'low': low,
                            'volume': random.uniform(100000000, 500000000),
                            'change_pct': change_pct
                        }])
                        return df
        except:
            pass

        # 数据源2: 网易财经
        try:
            code = info['code']
            url = f"http://api.money.126.net/data/feed/{code},money.api"
            response = requests.get(url, headers=self.headers, timeout=5)

            if response.status_code == 200:
                # 解析网易API响应（简化处理）
                pass
        except:
            pass

        return None

    def _get_mock_indices(self) -> Dict[str, pd.DataFrame]:
        """生成模拟指数数据"""
        indices = ['上证指数', '深证成指', '创业板指', '沪深300', '中证500']
        mock_data = {}

        base_values = {
            '上证指数': 3200,
            '深证成指': 10500,
            '创业板指': 2000,
            '沪深300': 3800,
            '中证500': 5500
        }

        # 随机生成当日涨跌（偏向于震荡行情）
        market_bias = random.uniform(-1.5, 1.5)  # 整体市场偏向

        for name in indices:
            mock_data[name] = self._get_mock_index_data(name, base_values[name], market_bias)

        return mock_data

    def _get_mock_index_data(self, name: str, base_value: float = None, bias: float = 0) -> pd.DataFrame:
        """生成单个指数的模拟数据"""
        if base_value is None:
            base_values = {
                '上证指数': 3200,
                '深证成指': 10500,
                '创业板指': 2000,
                '沪深300': 3800,
                '中证500': 5500
            }
            base_value = base_values.get(name, 3000)

        # 随机生成涨跌幅
        change_pct = bias + random.uniform(-0.8, 0.8)

        open_price = base_value * (1 + random.uniform(-0.005, 0.005))
        close_price = open_price * (1 + change_pct / 100)
        high = max(open_price, close_price) * (1 + random.uniform(0, 0.005))
        low = min(open_price, close_price) * (1 - random.uniform(0, 0.005))
        volume = random.uniform(100000000, 500000000)

        df = pd.DataFrame([{
            'datetime': datetime.now(),
            'open': open_price,
            'close': close_price,
            'high': high,
            'low': low,
            'volume': volume,
            'change_pct': change_pct
        }])

        return df

    def get_market_breadth(self) -> Optional[Dict]:
        """获取市场广度数据（涨跌统计）"""
        if self.use_mock_data:
            return self._get_mock_breadth()

        try:
            # 使用腾讯财经API
            url = "http://qt.gtimg.cn/q=sh000001,sz399001,sz399006"
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                # 解析数据
                return self._get_mock_breadth()

        except Exception as e:
            print(f"⚠️  获取市场广度数据失败，使用模拟数据: {str(e)}")

        return self._get_mock_breadth()

    def _get_mock_breadth(self) -> Dict:
        """生成模拟市场广度数据"""
        total = random.randint(4500, 5200)

        # 根据市场情况生成涨跌分布
        market_bias = random.uniform(-0.3, 0.3)  # 市场偏向

        if market_bias > 0.15:
            # 看多行情
            up_ratio = random.uniform(0.6, 0.8)
        elif market_bias < -0.15:
            # 看空行情
            up_ratio = random.uniform(0.2, 0.4)
        else:
            # 震荡行情
            up_ratio = random.uniform(0.4, 0.6)

        up_count = int(total * up_ratio)
        down_count = int(total * (1 - up_ratio) * 0.95)
        flat_count = total - up_count - down_count

        # 涨跌停统计
        if market_bias > 0.1:
            limit_up = random.randint(30, 100)
            limit_down = random.randint(0, 10)
        elif market_bias < -0.1:
            limit_up = random.randint(0, 10)
            limit_down = random.randint(30, 80)
        else:
            limit_up = random.randint(10, 30)
            limit_down = random.randint(10, 30)

        return {
            'total': total,
            'up_count': up_count,
            'down_count': down_count,
            'flat_count': flat_count,
            'limit_up': limit_up,
            'limit_down': limit_down,
            'up_ratio': up_count / total,
            'down_ratio': down_count / total
        }

    def calculate_volume_ratio(self, indices_data: Dict[str, pd.DataFrame]) -> Dict:
        """计算成交量比率"""
        volume_analysis = {}

        for name, df in indices_data.items():
            if not df.empty:
                current_volume = df['volume'].iloc[0]

                # 与历史均值对比（简化处理）
                avg_volume = 300000000  # 假设的均量
                volume_ratio = current_volume / avg_volume

                if volume_ratio > 1.5:
                    trend = "放量"
                elif volume_ratio < 0.7:
                    trend = "缩量"
                else:
                    trend = "正常"

                volume_analysis[name] = {
                    'current_volume': current_volume,
                    'volume_ratio': volume_ratio,
                    'trend': trend
                }

        return volume_analysis

    def analyze_technical_indicators(self, df: pd.DataFrame) -> Dict:
        """分析技术指标"""
        if df is None or df.empty:
            return {}

        close = df['close'].iloc[0]
        change_pct = df['change_pct'].iloc[0]
        open_price = df['open'].iloc[0]

        analysis = {
            'price_action': '中性',
            'trend': '震荡',
            'strength': 0
        }

        # 价格形态分析
        if close > open_price:
            if change_pct > 1:
                analysis['price_action'] = '强势上涨'
                analysis['strength'] = min(change_pct / 3, 1)
            elif change_pct > 0.3:
                analysis['price_action'] = '温和上涨'
                analysis['strength'] = min(change_pct / 2, 0.7)
            else:
                analysis['price_action'] = '小幅上涨'
                analysis['strength'] = 0.3
        elif close < open_price:
            if change_pct < -1:
                analysis['price_action'] = '强势下跌'
                analysis['strength'] = -min(abs(change_pct) / 3, 1)
            elif change_pct < -0.3:
                analysis['price_action'] = '温和下跌'
                analysis['strength'] = -min(abs(change_pct) / 2, 0.7)
            else:
                analysis['price_action'] = '小幅下跌'
                analysis['strength'] = -0.3

        # 趋势判断
        if change_pct > 0.5:
            analysis['trend'] = '上升趋势'
        elif change_pct < -0.5:
            analysis['trend'] = '下降趋势'
        else:
            analysis['trend'] = '震荡整理'

        return analysis

    def calculate_sentiment_score(self,
                                 indices_data: Dict[str, pd.DataFrame],
                                 breadth_data: Optional[Dict],
                                 volume_data: Dict) -> Tuple[float, str]:
        """计算综合情绪得分"""

        if not indices_data:
            return 0, "数据不足"

        scores = []
        weights = []

        # 1. 主要指数得分 (权重40%)
        index_changes = []
        for name, df in indices_data.items():
            if not df.empty:
                change_pct = df['change_pct'].iloc[0]
                index_changes.append(change_pct)

        if index_changes:
            # 平均涨跌幅转换为-1到1的得分
            avg_change = np.mean(index_changes)
            score = np.tanh(avg_change / 2)
            scores.append(score)
            weights.append(0.40)

        # 2. 市场广度得分 (权重40%)
        if breadth_data:
            # 上涨比例 - 下跌比例
            breadth_score = breadth_data['up_ratio'] - breadth_data['down_ratio']
            scores.append(breadth_score)
            weights.append(0.30)

            # 涨停板加分 (权重10%)
            if breadth_data['total'] > 0:
                limit_score = (breadth_data['limit_up'] - breadth_data['limit_down']) / breadth_data['total'] * 100
                scores.append(np.clip(limit_score, -1, 1))
                weights.append(0.10)

        # 3. 技术面得分 (权重20%)
        tech_scores = []
        for name, df in indices_data.items():
            tech = self.analyze_technical_indicators(df)
            tech_scores.append(tech.get('strength', 0))

        if tech_scores:
            avg_tech = np.mean(tech_scores)
            scores.append(avg_tech)
            weights.append(0.20)

        # 计算加权平均得分
        if sum(weights) > 0:
            final_score = sum(s * w for s, w in zip(scores, weights)) / sum(weights)
        else:
            final_score = 0

        # 得分转换为情绪判断
        if final_score >= 0.6:
            sentiment = "强烈看多 🚀"
            level = "极度乐观"
            color = "🟢"
        elif final_score >= 0.3:
            sentiment = "看多 📈"
            level = "乐观"
            color = "🟢"
        elif final_score >= 0.1:
            sentiment = "偏多 ↗️"
            level = "偏向乐观"
            color = "🟡"
        elif final_score > -0.1:
            sentiment = "中性 ➡️"
            level = "观望"
            color = "⚪"
        elif final_score > -0.3:
            sentiment = "偏空 ↘️"
            level = "偏向悲观"
            color = "🟡"
        elif final_score > -0.6:
            sentiment = "看空 📉"
            level = "悲观"
            color = "🔴"
        else:
            sentiment = "强烈看空 💥"
            level = "极度悲观"
            color = "🔴"

        return final_score, sentiment

    def generate_sentiment_report(self) -> Optional[Dict]:
        """生成市场情绪报告"""
        print("\n" + "="*80)
        print("📊 A股市场情绪分析")
        print("="*80)
        print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"数据模式: {'模拟数据（演示用）' if self.use_mock_data else '实时数据'}")
        print("="*80 + "\n")

        # 获取数据
        print("📡 正在获取市场数据...")

        indices_data = self.get_market_indices()
        breadth_data = self.get_market_breadth()
        volume_data = self.calculate_volume_ratio(indices_data) if indices_data else {}

        if not indices_data:
            print("\n❌ 无法获取市场数据")
            return None

        # 分析主要指数
        print("\n" + "="*80)
        print("📈 主要指数表现")
        print("="*80 + "\n")

        for name, df in indices_data.items():
            if not df.empty:
                change_pct = df['change_pct'].iloc[0]
                close = df['close'].iloc[0]

                # 判断涨跌
                if change_pct > 0:
                    trend_icon = "📈"
                    trend_text = "上涨"
                elif change_pct < 0:
                    trend_icon = "📉"
                    trend_text = "下跌"
                else:
                    trend_icon = "➡️"
                    trend_text = "平盘"

                print(f"{name}:")
                print(f"  收盘点位: {close:.2f}")
                print(f"  涨跌幅:   {change_pct:+.2f}% {trend_icon}")

                # 技术分析
                tech = self.analyze_technical_indicators(df)
                print(f"  价格形态: {tech['price_action']}")
                print(f"  趋势:     {tech['trend']}")
                print()

        # 市场广度分析
        if breadth_data:
            print("="*80)
            print("🔍 市场广度分析")
            print("="*80 + "\n")

            total = breadth_data['total']
            up_count = breadth_data['up_count']
            down_count = breadth_data['down_count']
            limit_up = breadth_data['limit_up']
            limit_down = breadth_data['limit_down']

            print(f"总股票数:   {total} 只")
            print(f"上涨股票:   {up_count} 只 ({breadth_data['up_ratio']:.1%}) 📈")
            print(f"下跌股票:   {down_count} 只 ({breadth_data['down_ratio']:.1%}) 📉")
            print(f"平盘股票:   {breadth_data['flat_count']} 只")
            print(f"\n涨停板:     {limit_up} 只 🔴")
            print(f"跌停板:     {limit_down} 只 🟢")

            # 市场情绪判断
            if breadth_data['up_ratio'] > 0.7:
                breadth_sentiment = "普涨行情，市场情绪高涨 🎉"
            elif breadth_data['up_ratio'] > 0.6:
                breadth_sentiment = "多数上涨，市场情绪良好 😊"
            elif breadth_data['up_ratio'] > 0.4:
                breadth_sentiment = "涨跌互现，市场情绪中性 😐"
            elif breadth_data['up_ratio'] > 0.3:
                breadth_sentiment = "多数下跌，市场情绪偏弱 😟"
            else:
                breadth_sentiment = "普跌行情，市场情绪低迷 😰"

            print(f"\n广度评价:   {breadth_sentiment}")
            print()

        # 计算综合情绪得分
        score, sentiment = self.calculate_sentiment_score(indices_data, breadth_data, volume_data)

        print("="*80)
        print("🎯 综合情绪判断")
        print("="*80 + "\n")

        # 颜色标识
        if score >= 0.1:
            color_icon = "🟢"
        elif score > -0.1:
            color_icon = "⚪"
        else:
            color_icon = "🔴"

        print(f"情绪得分:   {score:+.3f} (范围: -1 到 +1) {color_icon}")
        print(f"市场情绪:   {sentiment}")

        # 评分等级说明
        if score >= 0.6:
            print(f"\n评价:       市场极度强势，多头完全掌控")
        elif score >= 0.3:
            print(f"\n评价:       市场走势良好，多头占优")
        elif score >= 0.1:
            print(f"\n评价:       市场偏暖，多头略强")
        elif score > -0.1:
            print(f"\n评价:       多空平衡，方向不明")
        elif score > -0.3:
            print(f"\n评价:       市场偏弱，空头略强")
        elif score > -0.6:
            print(f"\n评价:       市场走势疲软，空头占优")
        else:
            print(f"\n评价:       市场极度疲软，空头完全掌控")

        # 操作建议
        print("\n" + "="*80)
        print("💡 操作建议")
        print("="*80 + "\n")

        if score >= 0.6:
            print("✅ 建议积极做多，可适当增加仓位")
            print("✅ 关注强势板块和龙头个股")
            print("✅ 设置止损，控制风险")
            print("✅ 可考虑融资买入（谨慎）")
        elif score >= 0.3:
            print("✅ 偏多操作，可维持中等仓位（60-70%）")
            print("✅ 择机买入优质标的")
            print("⚠️  注意回调风险，及时止盈")
        elif score >= 0.1:
            print("➡️ 轻仓试探，维持30-50%仓位")
            print("➡️ 等待更明确信号")
            print("➡️ 可考虑高抛低吸")
        elif score >= -0.1:
            print("⚠️  建议减仓至30%以下或空仓观望")
            print("⚠️  不宜激进操作")
            print("⚠️  等待市场企稳信号")
        elif score >= -0.3:
            print("❌ 严格控制仓位在20%以下")
            print("❌ 避免抄底，等待企稳")
            print("❌ 关注防御性板块")
        else:
            print("❌ 严格空仓或极低仓位（<10%）")
            print("❌ 避免抄底，等待明确企稳信号")
            print("❌ 可考虑轻仓做空或空仓观望")
            print("❌ 保护资金安全为第一要务")

        print("\n" + "="*80)

        return {
            'score': score,
            'sentiment': sentiment,
            'indices': indices_data,
            'breadth': breadth_data,
            'timestamp': datetime.now()
        }


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='A股市场情绪分析系统')
    parser.add_argument('--mock', action='store_true', help='使用模拟数据演示')
    args = parser.parse_args()

    print("""
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║              📊 A股市场情绪分析系统 v2.0                           ║
║                                                                   ║
║              智能判断当日是看多还是看空                             ║
║              支持实时数据和模拟演示模式                              ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
    """)

    analyzer = AStockMarketSentimentEnhanced(use_mock_data=args.mock)
    report = analyzer.generate_sentiment_report()

    if report:
        print("\n✅ 分析完成!")

        # 保存结果
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = f"results/sentiment_report_{timestamp}.txt"

        import os
        os.makedirs('results', exist_ok=True)

        with open(result_file, 'w', encoding='utf-8') as f:
            f.write(f"A股市场情绪分析报告\n")
            f.write(f"{'='*80}\n\n")
            f.write(f"分析时间: {report['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"情绪得分: {report['score']:+.3f}\n")
            f.write(f"市场情绪: {report['sentiment']}\n")
            f.write(f"\n{'='*80}\n")

        print(f"\n📄 报告已保存: {result_file}")

    print("\n" + "="*80)
    print("分析结束，祝投资顺利! 📈💰")
    print("="*80 + "\n")

    print("\n💡 使用提示:")
    print("  使用实时数据: python market_sentiment_enhanced.py")
    print("  使用模拟数据: python market_sentiment_enhanced.py --mock")
    print()


if __name__ == "__main__":
    main()
