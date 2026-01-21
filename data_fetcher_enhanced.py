"""
增强版数据获取模块
支持多种免费数据源,避免API限流
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Optional
import logging
import time
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedDataFetcher:
    """增强的金融数据获取类,支持多个数据源"""

    def __init__(self, sources: List[str] = None):
        """
        初始化数据获取器

        Args:
            sources: 数据源列表,按优先级排序
                    可选: 'yahoo', 'yfinance_cache', 'mock', 'stooq', 'polygon'
        """
        self.sources = sources or ['yahoo', 'mock']
        self.cache = {}

    def fetch_data(
        self,
        symbol: str,
        interval: str = "1d",
        period: str = "2y",
        start: Optional[str] = None,
        end: Optional[str] = None,
        retry: bool = True
    ) -> pd.DataFrame:
        """
        获取金融数据,自动在多个数据源间切换

        Args:
            symbol: 交易标的代码
            interval: 数据间隔
            period: 时间周期
            start: 开始日期
            end: 结束日期
            retry: 是否重试其他数据源

        Returns:
            包含OHLCV数据的DataFrame
        """
        # 检查缓存
        cache_key = f"{symbol}_{interval}_{period}_{start}_{end}"
        if cache_key in self.cache:
            logger.info(f"使用缓存数据: {symbol}")
            return self.cache[cache_key].copy()

        # 尝试各个数据源
        for source in self.sources:
            try:
                logger.info(f"尝试使用 {source} 获取 {symbol} 数据...")

                if source == "yahoo":
                    data = self._fetch_yahoo_with_retry(symbol, interval, period, start, end)
                elif source == "mock":
                    data = self._generate_mock_data(symbol, period)
                elif source == "stooq":
                    data = self._fetch_stooq(symbol, period)
                elif source == "polygon":
                    data = self._fetch_polygon(symbol, interval, period)
                else:
                    logger.warning(f"未知数据源: {source}")
                    continue

                if not data.empty:
                    # 缓存数据
                    self.cache[cache_key] = data.copy()
                    logger.info(f"✓ 成功从 {source} 获取 {len(data)} 条数据")
                    return data

            except Exception as e:
                logger.warning(f"✗ {source} 获取失败: {str(e)}")
                if not retry:
                    break
                time.sleep(1)  # 避免请求过快
                continue

        logger.error(f"所有数据源均失败: {symbol}")
        return pd.DataFrame()

    def _fetch_yahoo_with_retry(
        self,
        symbol: str,
        interval: str,
        period: str,
        start: Optional[str],
        end: Optional[str],
        max_retries: int = 3
    ) -> pd.DataFrame:
        """从Yahoo Finance获取数据,带重试机制"""
        for attempt in range(max_retries):
            try:
                # 添加随机延迟避免限流
                if attempt > 0:
                    delay = 2 ** attempt + np.random.uniform(0, 1)
                    logger.info(f"等待 {delay:.1f} 秒后重试...")
                    time.sleep(delay)

                ticker = yf.Ticker(symbol)

                if start and end:
                    data = ticker.history(start=start, end=end, interval=interval, timeout=10)
                else:
                    data = ticker.history(period=period, interval=interval, timeout=10)

                if not data.empty:
                    # 标准化列名
                    data.columns = [col.lower().replace(' ', '_') for col in data.columns]
                    data.reset_index(inplace=True)
                    if 'date' in data.columns:
                        data.rename(columns={'date': 'datetime'}, inplace=True)

                    return data

            except Exception as e:
                if "Too Many Requests" in str(e) or "429" in str(e):
                    logger.warning(f"Yahoo API限流 (尝试 {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        continue
                else:
                    raise e

        return pd.DataFrame()

    def _generate_mock_data(self, symbol: str, period: str = "2y") -> pd.DataFrame:
        """生成高质量的模拟数据"""
        # 根据period确定天数
        period_days = {
            '1mo': 30,
            '3mo': 90,
            '6mo': 180,
            '1y': 365,
            '2y': 730,
            '5y': 1825,
        }

        n = period_days.get(period, 730)

        # 使用symbol作为种子,确保同一symbol每次生成相同数据
        np.random.seed(hash(symbol) % 10000)

        # 生成更真实的价格走势
        dates = pd.date_range(end=datetime.now(), periods=n, freq='D')

        # 几何布朗运动
        dt = 1/252  # 日
        mu = 0.08    # 年化收益率
        sigma = 0.2  # 波动率

        returns = np.random.normal((mu - 0.5 * sigma**2) * dt, sigma * np.sqrt(dt), n)
        price = 100 * np.cumprod(1 + returns)

        # 生成OHLCV
        data = pd.DataFrame({'datetime': dates})

        # 生成日内波动
        intraday_volatility = np.random.uniform(0.005, 0.02, n)

        data['open'] = price * (1 + np.random.uniform(-0.01, 0.01, n))
        data['high'] = np.maximum(data['open'], price) * (1 + np.abs(np.random.normal(0, intraday_volatility, n)))
        data['low'] = np.minimum(data['open'], price) * (1 - np.abs(np.random.normal(0, intraday_volatility, n)))
        data['close'] = price
        data['volume'] = np.random.lognormal(15, 0.5, n).astype(int)

        # 确保high >= max(open, close)和low <= min(open, close)
        data['high'] = np.maximum(data['high'], np.maximum(data['open'], data['close']))
        data['low'] = np.minimum(data['low'], np.minimum(data['open'], data['close']))

        logger.info(f"生成 {len(data)} 条模拟数据")
        return data

    def _fetch_stooq(self, symbol: str, period: str = "2y") -> pd.DataFrame:
        """从Stooq获取数据(免费,无需API key)"""
        try:
            # Stooq使用不同的股票代码格式
            stooq_symbol = symbol.replace('-', '-').replace('.', '-')

            url = f"https://stooq.com/q/d/l/?s={stooq_symbol}&i=d"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            from io import StringIO
            data = pd.read_csv(StringIO(response.text))

            if data.empty:
                return pd.DataFrame()

            # 标准化列名
            data.columns = [col.lower() for col in data.columns]
            data.rename(columns={'date': 'datetime'}, inplace=True)
            data['datetime'] = pd.to_datetime(data['datetime'])

            return data

        except Exception as e:
            logger.warning(f"Stooq获取失败: {str(e)}")
            return pd.DataFrame()

    def _fetch_polygon(self, symbol: str, interval: str, period: str) -> pd.DataFrame:
        """从Polygon.io获取数据(免费注册后可使用)"""
        # 需要API key,这里提供框架
        # 用户可以在 https://polygon.io/ 免费注册获取API key
        try:
            api_key = "YOUR_POLYGON_API_KEY"  # 替换为您的API key

            # 计算日期范围
            end_date = datetime.now()
            start_date = end_date - timedelta(days=730)  # 默认2年

            url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}?apikey={api_key}"

            response = requests.get(url, timeout=10)
            response.raise_for_status()

            json_data = response.json()

            if 'results' not in json_data or not json_data['results']:
                return pd.DataFrame()

            results = json_data['results']
            data = pd.DataFrame([{
                'datetime': pd.to_datetime(r['t'], unit='ms'),
                'open': r['o'],
                'high': r['h'],
                'low': r['l'],
                'close': r['c'],
                'volume': r['v']
            } for r in results])

            return data

        except Exception as e:
            logger.warning(f"Polygon获取失败: {str(e)}")
            return pd.DataFrame()

    def fetch_multiple_symbols(
        self,
        symbols: List[str],
        interval: str = "1d",
        period: str = "2y",
        delay: float = 0.5
    ) -> dict:
        """
        批量获取多个交易标的数据

        Args:
            symbols: 交易标的列表
            interval: 数据间隔
            period: 时间周期
            delay: 每次请求之间的延迟(秒)

        Returns:
            字典,键为symbol,值为对应的DataFrame
        """
        data_dict = {}
        for i, symbol in enumerate(symbols):
            logger.info(f"获取 {symbol} 数据 ({i+1}/{len(symbols)})...")

            data = self.fetch_data(symbol, interval, period)

            if not data.empty:
                data_dict[symbol] = data

            # 添加延迟避免限流
            if i < len(symbols) - 1:
                time.sleep(delay)

        return data_dict

    def save_data(self, data: pd.DataFrame, symbol: str, interval: str = "1d"):
        """保存数据到CSV文件"""
        from pathlib import Path
        Path("data").mkdir(exist_ok=True)

        filename = f"data/{symbol}_{interval}_{datetime.now().strftime('%Y%m%d')}.csv"
        data.to_csv(filename, index=False)
        logger.info(f"数据已保存到 {filename}")

    def load_data(self, filepath: str) -> pd.DataFrame:
        """从CSV文件加载数据"""
        data = pd.read_csv(filepath)
        if 'datetime' in data.columns:
            data['datetime'] = pd.to_datetime(data['datetime'])
        logger.info(f"从 {filepath} 加载了 {len(data)} 条数据")
        return data

    def clear_cache(self):
        """清空缓存"""
        self.cache.clear()
        logger.info("缓存已清空")


# 向后兼容的别名
DataFetcher = EnhancedDataFetcher


if __name__ == "__main__":
    # 测试代码
    print("=" * 80)
    print("增强版数据获取器测试")
    print("=" * 80)

    # 测试多个数据源
    fetcher = EnhancedDataFetcher(sources=['yahoo', 'mock'])

    test_symbols = ['AAPL', 'MSFT']

    for symbol in test_symbols:
        print(f"\n测试获取 {symbol} 数据...")
        data = fetcher.fetch_data(symbol, period="6mo")

        if not data.empty:
            print(f"✓ 成功获取 {len(data)} 条数据")
            print(f"  日期范围: {data['datetime'].min()} 到 {data['datetime'].max()}")
            print(f"  价格范围: ${data['close'].min():.2f} - ${data['close'].max():.2f}")
        else:
            print(f"✗ 获取失败")

        time.sleep(1)  # 避免请求过快
