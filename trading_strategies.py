"""
交易策略模块
定义策略基类和具体策略实现
"""

import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class Signal(Enum):
    """交易信号枚举"""
    BUY = 1
    SELL = -1
    HOLD = 0


class BaseStrategy(ABC):
    """策略基类"""

    def __init__(self, name: str, parameters: Dict = None):
        """
        初始化策略

        Args:
            name: 策略名称
            parameters: 策略参数
        """
        self.name = name
        self.parameters = parameters or {}
        self.signals = []

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        生成交易信号

        Args:
            data: 包含价格和技术指标的DataFrame

        Returns:
            添加了信号列的DataFrame
        """
        pass

    def validate_data(self, data: pd.DataFrame) -> bool:
        """验证数据是否包含必要的列"""
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        return all(col in data.columns for col in required_columns)


class MovingAverageCrossover(BaseStrategy):
    """移动平均线交叉策略"""

    def __init__(self, short_window: int = 20, long_window: int = 50):
        """
        初始化MA交叉策略

        Args:
            short_window: 短期均线周期
            long_window: 长期均线周期
        """
        super().__init__(
            name="Moving Average Crossover",
            parameters={'short_window': short_window, 'long_window': long_window}
        )
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        生成MA交叉信号

        信号规则:
        - 短期均线上穿长期均线: 买入
        - 短期均线下穿长期均线: 卖出
        """
        if not self.validate_data(data):
            raise ValueError("数据缺少必要的列")

        df = data.copy()

        # 计算移动平均线
        df['ma_short'] = df['close'].rolling(window=self.short_window).mean()
        df['ma_long'] = df['close'].rolling(window=self.long_window).mean()

        # 生成信号
        df['ma_diff'] = df['ma_short'] - df['ma_long']
        df['signal'] = Signal.HOLD.value

        # 金叉买入
        df.loc[(df['ma_diff'] > 0) & (df['ma_diff'].shift(1) <= 0), 'signal'] = Signal.BUY.value

        # 死叉卖出
        df.loc[(df['ma_diff'] < 0) & (df['ma_diff'].shift(1) >= 0), 'signal'] = Signal.SELL.value

        logger.info(f"生成了 {len(df[df['signal'] != 0])} 个交易信号")
        return df


class MeanReversion(BaseStrategy):
    """均值回归策略"""

    def __init__(self, window: int = 20, entry_threshold: float = 2.0, exit_threshold: float = 0.5):
        """
        初始化均值回归策略

        Args:
            window: 移动窗口
            entry_threshold: 入场阈值(标准差倍数)
            exit_threshold: 出场阈值(标准差倍数)
        """
        super().__init__(
            name="Mean Reversion",
            parameters={'window': window, 'entry_threshold': entry_threshold, 'exit_threshold': exit_threshold}
        )
        self.window = window
        self.entry_threshold = entry_threshold
        self.exit_threshold = exit_threshold

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        生成均值回归信号

        信号规则:
        - 价格低于均值 - entry_threshold * 标准差: 买入
        - 价格高于均值 + entry_threshold * 标准差: 卖出
        - 价格回归到均值附近: 平仓
        """
        if not self.validate_data(data):
            raise ValueError("数据缺少必要的列")

        df = data.copy()

        # 计算均值和标准差
        df['mean'] = df['close'].rolling(window=self.window).mean()
        df['std'] = df['close'].rolling(window=self.window).std()
        df['z_score'] = (df['close'] - df['mean']) / df['std']

        df['signal'] = Signal.HOLD.value

        # 价格偏离过大,反向交易
        df.loc[df['z_score'] < -self.entry_threshold, 'signal'] = Signal.BUY.value
        df.loc[df['z_score'] > self.entry_threshold, 'signal'] = Signal.SELL.value

        # 回归均值后平仓
        df.loc[abs(df['z_score']) < self.exit_threshold, 'signal'] = Signal.HOLD.value

        logger.info(f"生成了 {len(df[df['signal'] != 0])} 个交易信号")
        return df


class MomentumStrategy(BaseStrategy):
    """动量策略"""

    def __init__(self, lookback: int = 20, threshold: float = 0.02):
        """
        初始化动量策略

        Args:
            lookback: 回看周期
            threshold: 动量阈值
        """
        super().__init__(
            name="Momentum",
            parameters={'lookback': lookback, 'threshold': threshold}
        )
        self.lookback = lookback
        self.threshold = threshold

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        生成动量信号

        信号规则:
        - 过去lookback期涨幅 > threshold: 买入
        - 过去lookback期跌幅 < -threshold: 卖出
        """
        if not self.validate_data(data):
            raise ValueError("数据缺少必要的列")

        df = data.copy()

        # 计算动量
        df['momentum'] = df['close'].pct_change(self.lookback)
        df['signal'] = Signal.HOLD.value

        # 动量向上买入
        df.loc[df['momentum'] > self.threshold, 'signal'] = Signal.BUY.value

        # 动量向下卖出
        df.loc[df['momentum'] < -self.threshold, 'signal'] = Signal.SELL.value

        logger.info(f"生成了 {len(df[df['signal'] != 0])} 个交易信号")
        return df


class RSIStrategy(BaseStrategy):
    """RSI策略"""

    def __init__(self, rsi_period: int = 14, oversold: float = 30, overbought: float = 70):
        """
        初始化RSI策略

        Args:
            rsi_period: RSI周期
            oversold: 超卖阈值
            overbought: 超买阈值
        """
        super().__init__(
            name="RSI",
            parameters={'rsi_period': rsi_period, 'oversold': oversold, 'overbought': overbought}
        )
        self.rsi_period = rsi_period
        self.oversold = oversold
        self.overbought = overbought

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        生成RSI信号

        信号规则:
        - RSI < oversold: 买入
        - RSI > overbought: 卖出
        """
        if not self.validate_data(data):
            raise ValueError("数据缺少必要的列")

        df = data.copy()

        # 计算RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()

        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))

        df['signal'] = Signal.HOLD.value

        # 超卖买入
        df.loc[df['rsi'] < self.oversold, 'signal'] = Signal.BUY.value

        # 超买卖出
        df.loc[df['rsi'] > self.overbought, 'signal'] = Signal.SELL.value

        logger.info(f"生成了 {len(df[df['signal'] != 0])} 个交易信号")
        return df


class MACDStrategy(BaseStrategy):
    """MACD策略"""

    def __init__(self, fast: int = 12, slow: int = 26, signal: int = 9):
        """
        初始化MACD策略

        Args:
            fast: 快线周期
            slow: 慢线周期
            signal: 信号线周期
        """
        super().__init__(
            name="MACD",
            parameters={'fast': fast, 'slow': slow, 'signal': signal}
        )
        self.fast = fast
        self.slow = slow
        self.signal_period = signal

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        生成MACD信号

        信号规则:
        - MACD线上穿信号线: 买入
        - MACD线下穿信号线: 卖出
        """
        if not self.validate_data(data):
            raise ValueError("数据缺少必要的列")

        df = data.copy()

        # 计算MACD
        ema_fast = df['close'].ewm(span=self.fast, adjust=False).mean()
        ema_slow = df['close'].ewm(span=self.slow, adjust=False).mean()

        df['macd'] = ema_fast - ema_slow
        df['macd_signal'] = df['macd'].ewm(span=self.signal_period, adjust=False).mean()
        df['macd_hist'] = df['macd'] - df['macd_signal']

        df['signal'] = Signal.HOLD.value

        # MACD金叉买入
        df.loc[(df['macd'] > df['macd_signal']) & (df['macd'].shift(1) <= df['macd_signal'].shift(1)), 'signal'] = Signal.BUY.value

        # MACD死叉卖出
        df.loc[(df['macd'] < df['macd_signal']) & (df['macd'].shift(1) >= df['macd_signal'].shift(1)), 'signal'] = Signal.SELL.value

        logger.info(f"生成了 {len(df[df['signal'] != 0])} 个交易信号")
        return df


class BollingerBandsStrategy(BaseStrategy):
    """布林带策略"""

    def __init__(self, window: int = 20, num_std: float = 2.0):
        """
        初始化布林带策略

        Args:
            window: 移动窗口
            num_std: 标准差倍数
        """
        super().__init__(
            name="Bollinger Bands",
            parameters={'window': window, 'num_std': num_std}
        )
        self.window = window
        self.num_std = num_std

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        生成布林带信号

        信号规则:
        - 价格触及下轨: 买入
        - 价格触及上轨: 卖出
        - 价格回归中轨: 平仓
        """
        if not self.validate_data(data):
            raise ValueError("数据缺少必要的列")

        df = data.copy()

        # 计算布林带
        df['bb_middle'] = df['close'].rolling(window=self.window).mean()
        df['bb_std'] = df['close'].rolling(window=self.window).std()
        df['bb_upper'] = df['bb_middle'] + (df['bb_std'] * self.num_std)
        df['bb_lower'] = df['bb_middle'] - (df['bb_std'] * self.num_std)

        df['signal'] = Signal.HOLD.value

        # 触及下轨买入
        df.loc[df['close'] <= df['bb_lower'], 'signal'] = Signal.BUY.value

        # 触及上轨卖出
        df.loc[df['close'] >= df['bb_upper'], 'signal'] = Signal.SELL.value

        logger.info(f"生成了 {len(df[df['signal'] != 0])} 个交易信号")
        return df


class MultiIndicatorStrategy(BaseStrategy):
    """多指标组合策略"""

    def __init__(self, strategies: List[BaseStrategy], consensus_threshold: float = 0.6):
        """
        初始化多指标策略

        Args:
            strategies: 策略列表
            consensus_threshold: 共识阈值(0.5-1.0)
        """
        super().__init__(
            name="Multi-Indicator Strategy",
            parameters={'consensus_threshold': consensus_threshold}
        )
        self.strategies = strategies
        self.consensus_threshold = consensus_threshold

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        基于多个策略的共识生成信号

        信号规则:
        - 当consensus_threshold比例的策略都给出相同信号时,才执行
        """
        df = data.copy()
        df['signal'] = Signal.HOLD.value

        # 收集所有策略的信号
        all_signals = pd.DataFrame(index=df.index)
        for strategy in self.strategies:
            df_with_signals = strategy.generate_signals(df)
            all_signals[strategy.name] = df_with_signals['signal']

        # 计算共识
        buy_count = (all_signals == Signal.BUY.value).sum(axis=1)
        sell_count = (all_signals == Signal.SELL.value).sum(axis=1)
        total_strategies = len(self.strategies)

        # 基于阈值生成信号
        buy_threshold = int(total_strategies * self.consensus_threshold)
        sell_threshold = int(total_strategies * self.consensus_threshold)

        df.loc[buy_count >= buy_threshold, 'signal'] = Signal.BUY.value
        df.loc[sell_count >= sell_threshold, 'signal'] = Signal.SELL.value

        logger.info(f"生成了 {len(df[df['signal'] != 0])} 个交易信号")
        return df


if __name__ == "__main__":
    # 测试代码
    from data_fetcher import DataFetcher

    # 获取数据
    fetcher = DataFetcher()
    data = fetcher.fetch_data("AAPL", period="1y")

    # 测试各个策略
    strategies = [
        MovingAverageCrossover(20, 50),
        MeanReversion(20, 2.0, 0.5),
        MomentumStrategy(20, 0.02),
        RSIStrategy(14, 30, 70),
        MACDStrategy(12, 26, 9),
        BollingerBandsStrategy(20, 2.0)
    ]

    for strategy in strategies:
        print(f"\n测试策略: {strategy.name}")
        result = strategy.generate_signals(data)
        signal_counts = result['signal'].value_counts()
        print(f"买入信号: {signal_counts.get(1, 0)}")
        print(f"卖出信号: {signal_counts.get(-1, 0)}")
