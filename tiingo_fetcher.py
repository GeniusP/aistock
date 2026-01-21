#!/usr/bin/env python3
"""
Tiingo API数据获取模块
支持美股、ETF、加密货币等多种金融数据
"""

import pandas as pd
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import time


class TiingoDataFetcher:
    """Tiingo API数据获取器"""

    def __init__(self, api_key: str = "ef36156b72b04df949358dd625686d9e2ba728f6"):
        """
        初始化Tiingo数据获取器

        Args:
            api_key: Tiingo API密钥
        """
        self.api_key = api_key
        self.base_url = "https://api.tiingo.com/tiingo"
        self.headers = {
            'Content-Type': 'application/json'
        }

    def get_eod_data(self,
                     ticker: str,
                     start_date: Optional[str] = None,
                     end_date: Optional[str] = None,
                     frequency: str = "daily") -> pd.DataFrame:
        """
        获取日线数据（EOD - End of Day）

        Args:
            ticker: 股票代码，如 "AAPL"
            start_date: 开始日期，格式 "YYYY-MM-DD"
            end_date: 结束日期，格式 "YYYY-MM-DD"
            frequency: 频率，可选 "daily", "weekly", "monthly"

        Returns:
            包含OHLCV数据的DataFrame
        """
        # 设置默认日期范围
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date:
            # 默认获取1年数据
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

        # 构建请求URL
        url = f"{self.base_url}/daily/{ticker}/prices"

        params = {
            'startDate': start_date,
            'endDate': end_date,
            'frequency': frequency,
            'format': 'json',
            'token': self.api_key  # Tiingo使用token参数
        }

        try:
            print(f"📡 正在从Tiingo获取 {ticker} 的数据...")
            response = requests.get(url, headers=self.headers, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()

                if not data:
                    print(f"⚠️  未获取到 {ticker} 的数据")
                    return pd.DataFrame()

                # 转换为DataFrame
                df = pd.DataFrame(data)

                # 重命名列
                df = df.rename(columns={
                    'date': 'datetime',
                    'open': 'open',
                    'high': 'high',
                    'low': 'low',
                    'close': 'close',
                    'volume': 'volume',
                    'adjClose': 'adj_close'
                })

                # 选择需要的列
                df = df[['datetime', 'open', 'high', 'low', 'close', 'volume']]

                # 转换日期格式
                df['datetime'] = pd.to_datetime(df['datetime'])

                # 按日期排序
                df = df.sort_values('datetime').reset_index(drop=True)

                # 确保数值类型
                for col in ['open', 'high', 'low', 'close', 'volume']:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

                print(f"✅ 成功获取 {len(df)} 条数据")
                print(f"   日期范围: {df['datetime'].iloc[0]} 到 {df['datetime'].iloc[-1]}")
                print(f"   价格范围: {df['close'].min():.2f} - {df['close'].max():.2f}")

                return df

            elif response.status_code == 401:
                print("❌ API密钥无效，请检查您的Tiingo API密钥")
                return pd.DataFrame()
            elif response.status_code == 404:
                print(f"❌ 未找到股票代码 {ticker}")
                return pd.DataFrame()
            elif response.status_code == 429:
                print("⚠️  API调用频率超限，请稍后重试")
                return pd.DataFrame()
            else:
                print(f"❌ 获取数据失败: HTTP {response.status_code}")
                print(f"   错误信息: {response.text}")
                return pd.DataFrame()

        except requests.exceptions.Timeout:
            print("❌ 请求超时，请检查网络连接")
            return pd.DataFrame()
        except requests.exceptions.ConnectionError:
            print("❌ 网络连接错误，请检查网络设置")
            return pd.DataFrame()
        except Exception as e:
            print(f"❌ 获取数据时出错: {str(e)}")
            return pd.DataFrame()

    def get_realtime_quote(self, ticker: str) -> Optional[Dict]:
        """
        获取实时报价

        Args:
            ticker: 股票代码

        Returns:
            包含实时报价的字典
        """
        url = f"{self.base_url}/iex/{ticker}"

        params = {
            'token': self.api_key
        }

        # 不使用headers中的Authorization，改用token参数

        try:
            response = requests.get(url, params=params, timeout=5)

            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    data = data[0]

                quote = {
                    'ticker': ticker,
                    'last': data.get('last'),
                    'bid': data.get('bidPrice'),
                    'ask': data.get('askPrice'),
                    'volume': data.get('volume'),
                    'timestamp': datetime.now()
                }

                return quote
            else:
                print(f"❌ 获取实时报价失败: HTTP {response.status_code}")
                return None

        except Exception as e:
            print(f"❌ 获取实时报价时出错: {str(e)}")
            return None

    def get_crypto_data(self,
                       ticker: str = "btcusd",
                       start_date: Optional[str] = None,
                       end_date: Optional[str] = None) -> pd.DataFrame:
        """
        获取加密货币数据

        Args:
            ticker: 加密货币代码，如 "btcusd", "ethusd"
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            包含加密货币数据的DataFrame
        """
        # 设置默认日期范围
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        url = f"{self.base_url}/crypto/prices"

        params = {
            'tickers': ticker,
            'startDate': start_date,
            'endDate': end_date,
            'format': 'json',
            'resampleFreq': '1day',
            'token': self.api_key
        }

        try:
            print(f"📡 正在从Tiingo获取 {ticker.upper()} 加密货币数据...")

            response = requests.get(
                url,
                params=params,
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()

                # 处理返回的数据
                # Tiingo加密货币数据格式可能不同，需要根据实际情况调整
                if isinstance(data, list) and len(data) > 0:
                    price_data = data[0].get('priceData', [])

                    if price_data:
                        df = pd.DataFrame(price_data)

                        df = df.rename(columns={
                            'date': 'datetime',
                            'open': 'open',
                            'high': 'high',
                            'low': 'low',
                            'close': 'close',
                            'volume': 'volume'
                        })

                        df['datetime'] = pd.to_datetime(df['datetime'])

                        for col in ['open', 'high', 'low', 'close', 'volume']:
                            if col in df.columns:
                                df[col] = pd.to_numeric(df[col], errors='coerce')

                        print(f"✅ 成功获取 {len(df)} 条加密货币数据")
                        return df

                print("⚠️  加密货币数据格式未知")
                return pd.DataFrame()

            else:
                print(f"❌ 获取加密货币数据失败: HTTP {response.status_code}")
                return pd.DataFrame()

        except Exception as e:
            print(f"❌ 获取加密货币数据时出错: {str(e)}")
            return pd.DataFrame()

    def get_ticker_metadata(self, ticker: str) -> Optional[Dict]:
        """
        获取股票元数据

        Args:
            ticker: 股票代码

        Returns:
            包含股票元数据的字典
        """
        url = f"{self.base_url}/daily/{ticker}"

        params = {
            'token': self.api_key
        }

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=5)

            if response.status_code == 200:
                data = response.json()

                metadata = {
                    'ticker': data.get('ticker'),
                    'name': data.get('name'),
                    'description': data.get('description'),
                    'exchange': data.get('exchangeCode'),
                    'currency': data.get('currency'),
                    'start_date': data.get('startDate'),
                    'end_date': data.get('endDate')
                }

                return metadata
            else:
                print(f"❌ 获取元数据失败: HTTP {response.status_code}")
                return None

        except Exception as e:
            print(f"❌ 获取元数据时出错: {str(e)}")
            return None

    def search_tickers(self, query: str) -> List[Dict]:
        """
        搜索股票代码

        Args:
            query: 搜索关键词

        Returns:
            匹配的股票列表
        """
        url = f"{self.base_url}/tickers"

        params = {
            'search': query,
            'token': self.api_key
        }

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=5)

            if response.status_code == 200:
                data = response.json()
                return data
            else:
                print(f"❌ 搜索失败: HTTP {response.status_code}")
                return []

        except Exception as e:
            print(f"❌ 搜索时出错: {str(e)}")
            return []


def test_tiingo():
    """测试Tiingo API"""
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║              📊 Tiingo API 测试                                   ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
    """)

    # 初始化
    fetcher = TiingoDataFetcher()

    print(f"🔑 API密钥: {fetcher.api_key[:20]}...")
    print()

    # 测试1: 获取股票数据
    print("="*80)
    print("测试1: 获取AAPL股票数据")
    print("="*80 + "\n")

    df = fetcher.get_eod_data("AAPL", frequency="daily")

    if not df.empty:
        print("\n📊 数据预览:")
        print(df.head())
        print("\n数据统计:")
        print(df.describe())

    # 测试2: 获取实时报价
    print("\n" + "="*80)
    print("测试2: 获取实时报价")
    print("="*80 + "\n")

    quote = fetcher.get_realtime_quote("AAPL")
    if quote:
        print("实时报价:")
        for key, value in quote.items():
            print(f"  {key}: {value}")

    # 测试3: 获取股票元数据
    print("\n" + "="*80)
    print("测试3: 获取股票元数据")
    print("="*80 + "\n")

    metadata = fetcher.get_ticker_metadata("AAPL")
    if metadata:
        print("股票信息:")
        for key, value in metadata.items():
            if value:
                print(f"  {key}: {value}")

    print("\n" + "="*80)
    print("✅ 测试完成!")
    print("="*80)


if __name__ == "__main__":
    test_tiingo()
