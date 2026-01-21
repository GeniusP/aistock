"""
技术指标计算模块
实现常用技术指标: MA, EMA, RSI, MACD, Bollinger Bands, ATR等
"""

import pandas as pd
import numpy as np
from typing import Tuple


class TechnicalIndicators:
    """技术指标计算类"""

    @staticmethod
    def sma(data: pd.Series, window: int) -> pd.Series:
        """
        简单移动平均线 (SMA)

        Args:
            data: 价格序列
            window: 窗口期

        Returns:
            SMA序列
        """
        return data.rolling(window=window).mean()

    @staticmethod
    def ema(data: pd.Series, window: int) -> pd.Series:
        """
        指数移动平均线 (EMA)

        Args:
            data: 价格序列
            window: 窗口期

        Returns:
            EMA序列
        """
        return data.ewm(span=window, adjust=False).mean()

    @staticmethod
    def rsi(data: pd.Series, window: int = 14) -> pd.Series:
        """
        相对强弱指标 (RSI)

        Args:
            data: 价格序列
            window: 窗口期

        Returns:
            RSI序列 (0-100)
        """
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    @staticmethod
    def macd(data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        MACD指标

        Args:
            data: 价格序列
            fast: 快线周期
            slow: 慢线周期
            signal: 信号线周期

        Returns:
            (MACD线, 信号线, 柱状图)
        """
        ema_fast = data.ewm(span=fast, adjust=False).mean()
        ema_slow = data.ewm(span=slow, adjust=False).mean()

        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line

        return macd_line, signal_line, histogram

    @staticmethod
    def bollinger_bands(data: pd.Series, window: int = 20, num_std: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        布林带

        Args:
            data: 价格序列
            window: 窗口期
            num_std: 标准差倍数

        Returns:
            (上轨, 中轨, 下轨)
        """
        middle = data.rolling(window=window).mean()
        std = data.rolling(window=window).std()
        upper = middle + (std * num_std)
        lower = middle - (std * num_std)

        return upper, middle, lower

    @staticmethod
    def atr(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> pd.Series:
        """
        平均真实波幅 (ATR)

        Args:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            window: 窗口期

        Returns:
            ATR序列
        """
        high_low = high - low
        high_close = np.abs(high - close.shift())
        low_close = np.abs(low - close.shift())

        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=window).mean()

        return atr

    @staticmethod
    def stochastic(high: pd.Series, low: pd.Series, close: pd.Series, k_window: int = 14, d_window: int = 3) -> Tuple[pd.Series, pd.Series]:
        """
        随机指标 (Stochastic Oscillator)

        Args:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            k_window: K值窗口期
            d_window: D值窗口期

        Returns:
            (%K, %D)
        """
        lowest_low = low.rolling(window=k_window).min()
        highest_high = high.rolling(window=k_window).max()

        k_percent = 100 * (close - lowest_low) / (highest_high - lowest_low)
        d_percent = k_percent.rolling(window=d_window).mean()

        return k_percent, d_percent

    @staticmethod
    def obv(close: pd.Series, volume: pd.Series) -> pd.Series:
        """
        能量潮指标 (OBV)

        Args:
            close: 收盘价序列
            volume: 成交量序列

        Returns:
            OBV序列
        """
        obv = pd.Series(index=close.index, dtype=float)
        obv.iloc[0] = volume.iloc[0]

        for i in range(1, len(close)):
            if close.iloc[i] > close.iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] + volume.iloc[i]
            elif close.iloc[i] < close.iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] - volume.iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i-1]

        return obv

    @staticmethod
    def williams_r(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> pd.Series:
        """
        威廉指标 (%R)

        Args:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            window: 窗口期

        Returns:
            %R序列 (-100到0)
        """
        highest_high = high.rolling(window=window).max()
        lowest_low = low.rolling(window=window).min()

        williams_r = -100 * (highest_high - close) / (highest_high - lowest_low)
        return williams_r

    @staticmethod
    def cci(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 20) -> pd.Series:
        """
        商品通道指标 (CCI)

        Args:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            window: 窗口期

        Returns:
            CCI序列
        """
        typical_price = (high + low + close) / 3
        sma = typical_price.rolling(window=window).mean()
        mad = typical_price.rolling(window=window).apply(lambda x: np.abs(x - x.mean()).mean())

        cci = (typical_price - sma) / (0.015 * mad)
        return cci

    @staticmethod
    def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """
        为DataFrame添加所有常用技术指标

        Args:
            df: 包含OHLCV数据的DataFrame

        Returns:
            添加了技术指标的DataFrame
        """
        df = df.copy()

        # 移动平均线
        df['sma_20'] = TechnicalIndicators.sma(df['close'], 20)
        df['sma_50'] = TechnicalIndicators.sma(df['close'], 50)
        df['ema_12'] = TechnicalIndicators.ema(df['close'], 12)
        df['ema_26'] = TechnicalIndicators.ema(df['close'], 26)

        # RSI
        df['rsi'] = TechnicalIndicators.rsi(df['close'])

        # MACD
        df['macd'], df['macd_signal'], df['macd_hist'] = TechnicalIndicators.macd(df['close'])

        # 布林带
        df['bb_upper'], df['bb_middle'], df['bb_lower'] = TechnicalIndicators.bollinger_bands(df['close'])
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        df['bb_pct'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])

        # ATR
        df['atr'] = TechnicalIndicators.atr(df['high'], df['low'], df['close'])

        # 随机指标
        df['stoch_k'], df['stoch_d'] = TechnicalIndicators.stochastic(df['high'], df['low'], df['close'])

        # OBV
        df['obv'] = TechnicalIndicators.obv(df['close'], df['volume'])

        # Williams %R
        df['williams_r'] = TechnicalIndicators.williams_r(df['high'], df['low'], df['close'])

        # CCI
        df['cci'] = TechnicalIndicators.cci(df['high'], df['low'], df['close'])

        return df


if __name__ == "__main__":
    # 测试代码
    import yfinance as yf

    # 获取测试数据
    data = yf.Ticker("AAPL").history(period="1y")
    data.columns = [col.lower() for col in data.columns]
    data.reset_index(inplace=True)

    # 添加技术指标
    data_with_indicators = TechnicalIndicators.add_all_indicators(data)

    print("添加的技术指标:")
    print(data_with_indicators.columns.tolist())
    print("\n最近5天的数据:")
    print(data_with_indicators[['datetime', 'close', 'sma_20', 'sma_50', 'rsi', 'macd']].tail())
