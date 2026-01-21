#!/usr/bin/env python3
"""
A股市场情绪分析模块
分析当日A股市场是看多还是看空
"""

import sys
sys.path.insert(0, '/Users/user/Desktop/量化ai')

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
from typing import Dict, Tuple, List


class AStockMarketSentiment:
    """A股市场情绪分析器"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

    def get_market_indices(self) -> Dict[str, pd.DataFrame]:
        """获取主要指数数据"""
        indices = {
            '上证指数': '000001',
            '深证成指': '399001',
            '创业板指': '399006',
            '沪深300': '000300',
            '中证500': '000905'
        }

        indices_data = {}

        # 使用东方财富API获取实时数据
        for name, code in indices.items():
            try:
                # 获取指数实时行情
                url = f"http://push2.eastmoney.com/api/qt/stock/klt?secid=1.{code}&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58&klt=101&fqt=0&end=20500101&lmt=1"

                response = requests.get(url, headers=self.headers, timeout=5)
                data = response.json()

                if data and 'data' in data and data['data']:
                    klines = data['data']['klines']
                    if klines:
                        latest = klines[0]
                        df = pd.DataFrame([{
                            'datetime': latest[0],
                            'open': float(latest[1]),
                            'close': float(latest[2]),
                            'high': float(latest[3]),
                            'low': float(latest[4]),
                            'volume': float(latest[5]),
                            'change_pct': float(latest[8]) if len(latest) > 8 else 0
                        }])
                        df['datetime'] = pd.to_datetime(df['datetime'])
                        indices_data[name] = df
                        print(f"✅ 获取 {name} 数据成功")
                else:
                    print(f"⚠️  {name} 数据获取失败")

            except Exception as e:
                print(f"❌ 获取 {name} 出错: {str(e)}")

        return indices_data

    def get_market_breadth(self) -> Dict:
        """获取市场广度数据（涨跌统计）"""
        try:
            # 使用东方财富API获取涨跌统计
            url = "http://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=5&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23&fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f26,f22,f33,f11,f62,f128,f136,f115,f152"

            response = requests.get(url, headers=self.headers, timeout=10)
            data = response.json()

            if data and 'data' in data and 'diff' in data['data']:
                stocks = data['data']['diff']

                up_count = 0
                down_count = 0
                flat_count = 0
                limit_up = 0
                limit_down = 0

                for stock in stocks:
                    change_pct = stock.get('f3', 0) / 100  # 涨跌幅
                    change_pct = float(change_pct) if change_pct else 0

                    if change_pct > 0:
                        up_count += 1
                    elif change_pct < 0:
                        down_count += 1
                    else:
                        flat_count += 1

                    # 涨跌停统计（约10%为涨跌停）
                    if change_pct >= 0.095:
                        limit_up += 1
                    elif change_pct <= -0.095:
                        limit_down += 1

                total = len(stocks)

                return {
                    'total': total,
                    'up_count': up_count,
                    'down_count': down_count,
                    'flat_count': flat_count,
                    'limit_up': limit_up,
                    'limit_down': limit_down,
                    'up_ratio': up_count / total if total > 0 else 0,
                    'down_ratio': down_count / total if total > 0 else 0
                }

        except Exception as e:
            print(f"❌ 获取市场广度数据出错: {str(e)}")

        return None

    def calculate_volume_ratio(self, indices_data: Dict[str, pd.DataFrame]) -> Dict:
        """计算成交量比率"""
        volume_analysis = {}

        for name, df in indices_data.items():
            if not df.empty:
                current_volume = df['volume'].iloc[0]

                # 简化处理：假设成交量均值为参考
                # 实际应用中应该获取历史成交量数据
                volume_analysis[name] = {
                    'current_volume': current_volume,
                    'volume_ratio': 1.0,  # 占位符
                    'trend': '正常'
                }

        return volume_analysis

    def analyze_technical_indicators(self, df: pd.DataFrame) -> Dict:
        """分析技术指标"""
        if df is None or df.empty:
            return {}

        close = df['close'].iloc[0]
        high = df['high'].iloc[0]
        low = df['low'].iloc[0]
        open_price = df['open'].iloc[0]
        change_pct = df['change_pct'].iloc[0]

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
                                 breadth_data: Dict,
                                 volume_data: Dict) -> Tuple[float, str]:
        """计算综合情绪得分"""

        if not indices_data or not breadth_data:
            return 0, "数据不足"

        scores = []
        weights = []

        # 1. 主要指数得分 (权重40%)
        for name, df in indices_data.items():
            if not df.empty:
                change_pct = df['change_pct'].iloc[0]
                # 涨跌幅转换为-1到1的得分
                score = np.tanh(change_pct / 2)  # 使用tanh函数归一化
                scores.append(score)
                weights.append(0.08)  # 5个指数，每个8%

        # 2. 市场广度得分 (权重30%)
        if breadth_data:
            # 上涨比例 - 下跌比例
            breadth_score = breadth_data['up_ratio'] - breadth_data['down_ratio']
            scores.append(breadth_score)
            weights.append(0.30)

            # 涨停板加分 (权重10%)
            limit_up_score = (breadth_data['limit_up'] - breadth_data['limit_down']) / 100
            scores.append(np.clip(limit_up_score, -1, 1))
            weights.append(0.10)

        # 3. 成交量得分 (权重20%)
        # 这里简化处理，实际应该对比历史均量
        scores.append(0)  # 占位符
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
        elif final_score >= 0.3:
            sentiment = "看多 📈"
            level = "乐观"
        elif final_score >= 0.1:
            sentiment = "偏多 ↗️"
            level = "偏向乐观"
        elif final_score > -0.1:
            sentiment = "中性 ➡️"
            level = "观望"
        elif final_score > -0.3:
            sentiment = "偏空 ↘️"
            level = "偏向悲观"
        elif final_score > -0.6:
            sentiment = "看空 📉"
            level = "悲观"
        else:
            sentiment = "强烈看空 💥"
            level = "极度悲观"

        return final_score, sentiment

    def generate_sentiment_report(self) -> Dict:
        """生成市场情绪报告"""
        print("\n" + "="*80)
        print("📊 A股市场情绪分析")
        print("="*80)
        print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80 + "\n")

        # 获取数据
        print("📡 正在获取市场数据...")

        indices_data = self.get_market_indices()
        breadth_data = self.get_market_breadth()
        volume_data = self.calculate_volume_ratio(indices_data) if indices_data else {}

        if not indices_data:
            print("\n❌ 无法获取市场数据，请检查网络连接")
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

        print(f"情绪得分:   {score:+.3f} (范围: -1 到 +1)")
        print(f"市场情绪:   {sentiment}")

        # 操作建议
        print("\n" + "="*80)
        print("💡 操作建议")
        print("="*80 + "\n")

        if score >= 0.6:
            print("✅ 建议积极做多，可适当增加仓位")
            print("✅ 关注强势板块和龙头个股")
            print("✅ 设置止损，控制风险")
        elif score >= 0.3:
            print("✅ 偏多操作，可维持中等仓位")
            print("✅ 择机买入优质标的")
            print("⚠️  注意回调风险")
        elif score >= 0.1:
            print("➡️ 轻仓试探，谨慎参与")
            print("➡️ 等待更明确信号")
        elif score >= -0.3:
            print("⚠️  建议减仓或空仓观望")
            print("⚠️  不宜激进操作")
            print("⚠️  等待市场企稳")
        else:
            print("❌ 严格控制仓位，以防守为主")
            print("❌ 避免抄底，等待企稳信号")
            print("❌ 可考虑轻仓做空或空仓观望")

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
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║              📊 A股市场情绪分析系统 v1.0                           ║
║                                                                   ║
║              智能判断当日是看多还是看空                             ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
    """)

    analyzer = AStockMarketSentiment()
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
            f.write(f"分析时间: {report['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"情绪得分: {report['score']:+.3f}\n")
            f.write(f"市场情绪: {report['sentiment']}\n")
            f.write("\n" + "="*80 + "\n")

        print(f"\n📄 报告已保存: {result_file}")

    print("\n" + "="*80)
    print("分析结束，祝投资顺利! 📈💰")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
