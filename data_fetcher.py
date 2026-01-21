"""
数据获取模块
支持多种数据源: Alpha Vantage, Yahoo Finance, Tiingo等
"""

import pandas as pd
import yfinance as yf
import requests
from datetime import datetime, timedelta
from typing import List, Optional
import logging
import time

# 导入Tiingo获取器
from tiingo_fetcher import TiingoDataFetcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataFetcher:
    """金融数据获取类"""

    def __init__(self, source: str = "tiingo", api_key: Optional[str] = None):
        """
        初始化数据获取器

        Args:
            source: 数据源 (tiingo, alpha_vantage, yahoo)
            api_key: API key (如果需要)
        """
        self.source = source

        # 设置默认API密钥
        if source == "tiingo":
            self.api_key = api_key or "ef36156b72b04df949358dd625686d9e2ba728f6"
            self.tiingo_fetcher = TiingoDataFetcher(self.api_key)
        elif source == "alpha_vantage":
            self.api_key = api_key or "RQMP1U6N9J2OMIWH"
        else:
            self.api_key = api_key

        self.base_url = "https://www.alphavantage.co/query"

    def fetch_data(
        self,
        symbol: str,
        interval: str = "1d",
        period: str = "2y",
        start: Optional[str] = None,
        end: Optional[str] = None
    ) -> pd.DataFrame:
        """
        获取金融数据

        Args:
            symbol: 交易标的代码
            interval: 数据间隔 (1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo)
            period: 时间周期 (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            start: 开始日期 (YYYY-MM-DD)
            end: 结束日期 (YYYY-MM-DD)

        Returns:
            包含OHLCV数据的DataFrame
        """
        try:
            if self.source == "tiingo":
                return self._fetch_tiingo(symbol, interval, period, start, end)
            elif self.source == "alpha_vantage":
                return self._fetch_alpha_vantage(symbol, interval, period, start, end)
            elif self.source == "yahoo":
                return self._fetch_yahoo(symbol, interval, period, start, end)
            else:
                raise ValueError(f"不支持的数据源: {self.source}")
        except Exception as e:
            logger.error(f"获取数据失败 {symbol}: {str(e)}")
            return pd.DataFrame()

    def _fetch_tiingo(
        self,
        symbol: str,
        interval: str,
        period: str,
        start: Optional[str],
        end: Optional[str]
    ) -> pd.DataFrame:
        """从Tiingo获取数据"""
        logger.info(f"从Tiingo获取 {symbol} 数据...")

        # 转换日期格式
        if start:
            start_date = pd.to_datetime(start).strftime("%Y-%m-%d")
        else:
            # 根据period计算开始日期
            period_days = {
                "1mo": 30,
                "3mo": 90,
                "6mo": 180,
                "1y": 365,
                "2y": 730
            }
            days = period_days.get(period, 365)
            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        if end:
            end_date = pd.to_datetime(end).strftime("%Y-%m-%d")
        else:
            end_date = datetime.now().strftime("%Y-%m-%d")

        # 转换interval到Tiingo格式
        frequency_map = {
            "1d": "daily",
            "1wk": "weekly",
            "1mo": "monthly"
        }
        frequency = frequency_map.get(interval, "daily")

        # 调用Tiingo获取器
        df = self.tiingo_fetcher.get_eod_data(
            ticker=symbol,
            start_date=start_date,
            end_date=end_date,
            frequency=frequency
        )

        if not df.empty:
            logger.info(f"成功从Tiingo获取 {len(df)} 条 {symbol} 数据")
        else:
            logger.warning(f"从Tiingo未获取到 {symbol} 的数据")

        return df

    def _fetch_alpha_vantage(
        self,
        symbol: str,
        interval: str,
        period: str,
        start: Optional[str],
        end: Optional[str]
    ) -> pd.DataFrame:
        """从Alpha Vantage获取数据"""
        logger.info(f"从Alpha Vantage获取 {symbol} 数据...")

        # Alpha Vantage免费版本限制: 每分钟5次请求
        # 添加延迟避免超限
        time.sleep(12)  # 等待12秒确保不超过限制

        # 映射interval到Alpha Vantage格式
        interval_map = {
            "1m": "1min",
            "5m": "5min",
            "15m": "15min",
            "30m": "30min",
            "1h": "60min",
            "1d": "daily",
            "1wk": "weekly",
            "1mo": "monthly"
        }

        av_interval = interval_map.get(interval, "daily")

        # 映射period到outputsize
        # compact = 最近100天, full = 完整历史(最多20年)
        if period in ["1y", "2y", "5y", "10y", "max"]:
            outputsize = "full"
        else:
            outputsize = "compact"

        params = {
            "function": "TIME_SERIES_DAILY" if av_interval == "daily" else "TIME_SERIES_INTRADAY",
            "symbol": symbol,
            "interval": av_interval if av_interval != "daily" else None,
            "outputsize": outputsize,
            "apikey": self.api_key
        }

        # 移除None值
        params = {k: v for k, v in params.items() if v is not None}

        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            # 检查错误信息
            if "Error Message" in data:
                logger.error(f"Alpha Vantage错误: {data['Error Message']}")
                return pd.DataFrame()

            if "Note" in data:
                logger.error(f"Alpha Vantage API调用限制: {data['Note']}")
                return pd.DataFrame()

            # 解析数据
            if av_interval == "daily":
                time_series = data.get("Time Series (Daily)", {})
            else:
                time_series = data.get(f"Time Series ({av_interval})", {})

            if not time_series:
                logger.warning(f"未获取到 {symbol} 的数据")
                return pd.DataFrame()

            # 转换为DataFrame
            df = pd.DataFrame.from_dict(time_series, orient='index')

            # 重命名列
            df.columns = [col.split('. ')[1].lower() for col in df.columns]
            df.index.name = 'datetime'
            df.reset_index(inplace=True)
            df['datetime'] = pd.to_datetime(df['datetime'])

            # 按日期排序
            df = df.sort_values('datetime')

            # 过滤日期范围
            if start:
                df = df[df['datetime'] >= pd.to_datetime(start)]
            if end:
                df = df[df['datetime'] <= pd.to_datetime(end)]

            # 限制数据量根据period
            if period == "1y" and len(df) > 365:
                df = df.tail(365)
            elif period == "2y" and len(df) > 730:
                df = df.tail(730)
            elif period == "6mo" and len(df) > 180:
                df = df.tail(180)
            elif period == "3mo" and len(df) > 90:
                df = df.tail(90)
            elif period == "1mo" and len(df) > 30:
                df = df.tail(30)

            logger.info(f"成功获取 {len(df)} 条 {symbol} 数据")
            return df

        except requests.exceptions.RequestException as e:
            logger.error(f"Alpha Vantage请求失败: {str(e)}")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Alpha Vantage数据处理失败: {str(e)}")
            return pd.DataFrame()

    def _fetch_yahoo(
        self,
        symbol: str,
        interval: str,
        period: str,
        start: Optional[str],
        end: Optional[str]
    ) -> pd.DataFrame:
        """从Yahoo Finance获取数据"""
        logger.info(f"从Yahoo Finance获取 {symbol} 数据...")

        ticker = yf.Ticker(symbol)

        if start and end:
            data = ticker.history(start=start, end=end, interval=interval)
        else:
            data = ticker.history(period=period, interval=interval)

        if data.empty:
            logger.warning(f"未获取到 {symbol} 的数据")
            return pd.DataFrame()

        # 标准化列名
        data.columns = [col.lower().replace(' ', '_') for col in data.columns]
        data.reset_index(inplace=True)
        data.rename(columns={'date': 'datetime', 'index': 'datetime'}, inplace=True)

        logger.info(f"成功获取 {len(data)} 条 {symbol} 数据")
        return data

    def fetch_multiple_symbols(
        self,
        symbols: List[str],
        interval: str = "1d",
        period: str = "2y"
    ) -> dict:
        """
        批量获取多个交易标的数据

        Args:
            symbols: 交易标的列表
            interval: 数据间隔
            period: 时间周期

        Returns:
            字典,键为symbol,值为对应的DataFrame
        """
        data_dict = {}
        for symbol in symbols:
            data = self.fetch_data(symbol, interval, period)
            if not data.empty:
                data_dict[symbol] = data
        return data_dict

    def save_data(self, data: pd.DataFrame, symbol: str, interval: str = "1d"):
        """保存数据到CSV文件"""
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


if __name__ == "__main__":
    # 测试代码
    fetcher = DataFetcher()
    data = fetcher.fetch_data("AAPL", interval="1d", period="1y")
    if not data.empty:
        print(data.head())
        print(f"\n数据形状: {data.shape}")
        print(f"\n数据列: {data.columns.tolist()}")
        fetcher.save_data(data, "AAPL")
