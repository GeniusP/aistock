"""
风险管理和仓位管理模块
实现止损止盈、仓位控制、风险指标计算等功能
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class PositionSizer:
    """仓位管理基类"""

    def calculate_position_size(
        self,
        portfolio_value: float,
        entry_price: float,
        stop_loss_price: Optional[float] = None,
        **kwargs
    ) -> int:
        """
        计算仓位大小

        Args:
            portfolio_value: 组合总价值
            entry_price: 入场价格
            stop_loss_price: 止损价格 (可选)
            **kwargs: 其他参数

        Returns:
            建议持仓数量
        """
        pass


class FixedRatioSizer(PositionSizer):
    """固定比例仓位管理"""

    def __init__(self, ratio: float = 0.1):
        """
        初始化固定比例仓位管理

        Args:
            ratio: 每次交易使用的资金比例 (0-1)
        """
        self.ratio = ratio

    def calculate_position_size(
        self,
        portfolio_value: float,
        entry_price: float,
        stop_loss_price: Optional[float] = None,
        **kwargs
    ) -> int:
        """使用固定比例计算仓位"""
        capital = portfolio_value * self.ratio
        quantity = int(capital / entry_price)
        return quantity


class KellyCriterionSizer(PositionSizer):
    """凯利公式仓位管理"""

    def __init__(self, win_rate: float = 0.55, avg_win: float = 0.05, avg_loss: float = 0.04):
        """
        初始化凯利公式仓位管理

        Args:
            win_rate: 胜率
            avg_win: 平均盈利比例
            avg_loss: 平均亏损比例
        """
        self.win_rate = win_rate
        self.avg_win = avg_win
        self.avg_loss = avg_loss

    def calculate_position_size(
        self,
        portfolio_value: float,
        entry_price: float,
        stop_loss_price: Optional[float] = None,
        **kwargs
    ) -> int:
        """
        使用凯利公式计算仓位

        Kelly % = (b*p - q) / b
        其中:
        b = 盈亏比 (avg_win / avg_loss)
        p = 胜率
        q = 败率 (1-p)
        """
        b = self.avg_win / self.avg_loss if self.avg_loss != 0 else 1
        p = self.win_rate
        q = 1 - p

        kelly_fraction = (b * p - q) / b

        # 保守起见,使用凯利值的一半
        kelly_fraction = max(0, min(kelly_fraction, 0.25))  # 限制在0-25%之间

        capital = portfolio_value * kelly_fraction
        quantity = int(capital / entry_price)

        return quantity


class ATRBasedSizer(PositionSizer):
    """基于ATR的仓位管理"""

    def __init__(self, atr_multiplier: float = 2.0, risk_per_trade: float = 0.02):
        """
        初始化ATR仓位管理

        Args:
            atr_multiplier: ATR倍数
            risk_per_trade: 每笔交易风险比例
        """
        self.atr_multiplier = atr_multiplier
        self.risk_per_trade = risk_per_trade

    def calculate_position_size(
        self,
        portfolio_value: float,
        entry_price: float,
        stop_loss_price: Optional[float] = None,
        atr: Optional[float] = None,
        **kwargs
    ) -> int:
        """
        使用ATR计算仓位

        仓位规模 = (账户价值 * 风险比例) / (ATR * 倍数)
        """
        if atr is None:
            logger.warning("ATR未提供,使用固定比例")
            return int(portfolio_value * 0.1 / entry_price)

        risk_amount = portfolio_value * self.risk_per_trade
        stop_distance = atr * self.atr_multiplier

        quantity = int(risk_amount / stop_distance)
        return quantity


class VolatilityTargetSizer(PositionSizer):
    """波动率目标仓位管理"""

    def __init__(self, target_volatility: float = 0.15, lookback: int = 20):
        """
        初始化波动率目标仓位管理

        Args:
            target_volatility: 目标年化波动率
            lookback: 波动率计算窗口
        """
        self.target_volatility = target_volatility
        self.lookback = lookback

    def calculate_position_size(
        self,
        portfolio_value: float,
        entry_price: float,
        stop_loss_price: Optional[float] = None,
        historical_data: Optional[pd.Series] = None,
        **kwargs
    ) -> int:
        """
        基于波动率目标计算仓位

        仓位 = 目标波动率 / 当前实现波动率
        """
        if historical_data is None or len(historical_data) < self.lookback:
            logger.warning("历史数据不足,使用固定比例")
            return int(portfolio_value * 0.1 / entry_price)

        # 计算已实现波动率
        returns = historical_data.pct_change().dropna()
        realized_vol = returns.tail(self.lookback).std() * np.sqrt(252)

        # 计算目标仓位比例
        if realized_vol > 0:
            target_ratio = self.target_volatility / realized_vol
            target_ratio = max(0.1, min(target_ratio, 1.0))  # 限制在10%-100%
        else:
            target_ratio = 0.5

        capital = portfolio_value * target_ratio
        quantity = int(capital / entry_price)

        return quantity


class RiskManager:
    """风险管理类"""

    def __init__(
        self,
        max_position_size: float = 0.2,
        max_total_position: float = 0.8,
        max_drawdown: float = 0.15,
        stop_loss: float = 0.02,
        take_profit: float = 0.05
    ):
        """
        初始化风险管理器

        Args:
            max_position_size: 单个标的最大仓位比例
            max_total_position: 总体最大仓位比例
            max_drawdown: 最大回撤限制
            stop_loss: 止损比例
            take_profit: 止盈比例
        """
        self.max_position_size = max_position_size
        self.max_total_position = max_total_position
        self.max_drawdown = max_drawdown
        self.stop_loss = stop_loss
        self.take_profit = take_profit

        self.peak_equity = 0
        self.current_positions: Dict[str, float] = {}  # {symbol: value}

    def check_entry_conditions(
        self,
        symbol: str,
        proposed_value: float,
        portfolio_value: float
    ) -> Tuple[bool, str]:
        """
        检查入场条件

        Args:
            symbol: 交易标的
            proposed_value: 建议持仓价值
            portfolio_value: 组合总价值

        Returns:
            (是否允许, 原因说明)
        """
        # 检查单个标的仓位
        current_position = self.current_positions.get(symbol, 0)
        new_position = current_position + proposed_value
        position_ratio = new_position / portfolio_value if portfolio_value > 0 else 0

        if position_ratio > self.max_position_size:
            return False, f"超过单个标的最大仓位限制 {self.max_position_size:.1%}"

        # 检查总仓位
        total_position = sum(self.current_positions.values()) + proposed_value
        total_ratio = total_position / portfolio_value if portfolio_value > 0 else 0

        if total_ratio > self.max_total_position:
            return False, f"超过总体最大仓位限制 {self.max_total_position:.1%}"

        return True, "通过风险检查"

    def check_exit_conditions(
        self,
        entry_price: float,
        current_price: float,
        entry_date: pd.Timestamp,
        current_date: pd.Timestamp,
        position_type: str = "long"
    ) -> Tuple[bool, str]:
        """
        检查出场条件 (止损止盈)

        Args:
            entry_price: 入场价格
            current_price: 当前价格
            entry_date: 入场日期
            current_date: 当前日期
            position_type: 持仓类型 (long/short)

        Returns:
            (是否应该平仓, 原因说明)
        """
        if position_type == "long":
            pnl_pct = (current_price - entry_price) / entry_price

            if pnl_pct <= -self.stop_loss:
                return True, f"触发止损: 亏损 {pnl_pct:.2%}"

            if pnl_pct >= self.take_profit:
                return True, f"触发止盈: 盈利 {pnl_pct:.2%}"

        elif position_type == "short":
            pnl_pct = (entry_price - current_price) / entry_price

            if pnl_pct <= -self.stop_loss:
                return True, f"触发止损: 亏损 {pnl_pct:.2%}"

            if pnl_pct >= self.take_profit:
                return True, f"触发止盈: 盈利 {pnl_pct:.2%}"

        return False, "持有中"

    def check_drawdown_limit(self, current_equity: float) -> Tuple[bool, str]:
        """
        检查回撤限制

        Args:
            current_equity: 当前权益

        Returns:
            (是否超过限制, 说明)
        """
        if current_equity > self.peak_equity:
            self.peak_equity = current_equity

        drawdown = (current_equity - self.peak_equity) / self.peak_equity if self.peak_equity > 0 else 0

        if drawdown < -self.max_drawdown:
            return True, f"触发最大回撤限制: {drawdown:.2%}"

        return False, f"当前回撤: {drawdown:.2%}"

    def update_position(self, symbol: str, value: float):
        """更新持仓信息"""
        self.current_positions[symbol] = value

    def close_position(self, symbol: str):
        """平仓并移除持仓"""
        if symbol in self.current_positions:
            del self.current_positions[symbol]


class RiskMetrics:
    """风险指标计算类"""

    @staticmethod
    def calculate_var(returns: pd.Series, confidence_level: float = 0.95) -> float:
        """
        计算风险价值 (VaR)

        Args:
            returns: 收益率序列
            confidence_level: 置信水平

        Returns:
            VaR值 (负数表示损失)
        """
        return np.percentile(returns, (1 - confidence_level) * 100)

    @staticmethod
    def calculate_cvar(returns: pd.Series, confidence_level: float = 0.95) -> float:
        """
        计算条件风险价值 (CVaR/Expected Shortfall)

        Args:
            returns: 收益率序列
            confidence_level: 置信水平

        Returns:
            CVaR值
        """
        var = RiskMetrics.calculate_var(returns, confidence_level)
        return returns[returns <= var].mean()

    @staticmethod
    def calculate_max_drawdown(equity_curve: pd.Series) -> Dict:
        """
        计算最大回撤

        Args:
            equity_curve: 权益曲线

        Returns:
            包含回撤指标的字典
        """
        cummax = equity_curve.cummax()
        drawdown = (equity_curve - cummax) / cummax

        max_dd = drawdown.min()
        max_dd_date = drawdown.idxmin()

        # 计算回撤持续时间
        is_drawdown = drawdown < 0
        drawdown_periods = drawdown[is_drawdown]

        if len(drawdown_periods) > 0:
            # 找到最长的回撤期
            longest_dd_duration = 0
            current_duration = 0
            for dd in drawdown:
                if dd < 0:
                    current_duration += 1
                    longest_dd_duration = max(longest_dd_duration, current_duration)
                else:
                    current_duration = 0
        else:
            longest_dd_duration = 0

        return {
            'max_drawdown': max_dd,
            'max_drawdown_date': max_dd_date,
            'longest_drawdown_duration': longest_dd_duration
        }

    @staticmethod
    def calculate_calmar_ratio(annual_return: float, max_drawdown: float) -> float:
        """
        计算卡玛比率

        Args:
            annual_return: 年化收益率
            max_drawdown: 最大回撤 (绝对值)

        Returns:
            卡玛比率
        """
        if abs(max_drawdown) < 1e-6:
            return 0
        return annual_return / abs(max_drawdown)

    @staticmethod
    def calculate_sortino_ratio(returns: pd.Series, risk_free_rate: float = 0.0) -> float:
        """
        计算索提诺比率

        Args:
            returns: 收益率序列
            risk_free_rate: 无风险利率 (年化)

        Returns:
            索提诺比率
        """
        excess_returns = returns - risk_free_rate / 252
        downside_returns = excess_returns[excess_returns < 0]

        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return 0

        return np.sqrt(252) * excess_returns.mean() / downside_returns.std()

    @staticmethod
    def calculate_information_ratio(returns: pd.Series, benchmark_returns: pd.Series) -> float:
        """
        计算信息比率

        Args:
            returns: 策略收益率
            benchmark_returns: 基准收益率

        Returns:
            信息比率
        """
        excess_returns = returns - benchmark_returns

        if excess_returns.std() == 0:
            return 0

        return np.sqrt(252) * excess_returns.mean() / excess_returns.std()


if __name__ == "__main__":
    # 测试仓位管理
    portfolio_value = 100000
    entry_price = 150

    print("=== 测试仓位管理策略 ===")

    sizers = [
        FixedRatioSizer(ratio=0.2),
        KellyCriterionSizer(win_rate=0.55, avg_win=0.05, avg_loss=0.03),
        ATRBasedSizer(atr_multiplier=2, risk_per_trade=0.02),
        VolatilityTargetSizer(target_volatility=0.15)
    ]

    for sizer in sizers:
        quantity = sizer.calculate_position_size(
            portfolio_value=portfolio_value,
            entry_price=entry_price,
            atr=5.0
        )
        print(f"{sizer.__class__.__name__}: {quantity} 股 (价值 ${quantity * entry_price:,.2f})")

    # 测试风险管理
    print("\n=== 测试风险管理 ===")
    risk_manager = RiskManager(max_position_size=0.2, max_total_position=0.8)

    allowed, reason = risk_manager.check_entry_conditions("AAPL", 15000, portfolio_value)
    print(f"入场检查: {allowed} - {reason}")

    should_exit, reason = risk_manager.check_exit_conditions(150, 145, pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-10"))
    print(f"出场检查: {should_exit} - {reason}")

    # 测试风险指标
    print("\n=== 测试风险指标 ===")
    returns = pd.Series(np.random.randn(252) * 0.02)  # 模拟收益率

    var_95 = RiskMetrics.calculate_var(returns, 0.95)
    cvar_95 = RiskMetrics.calculate_cvar(returns, 0.95)
    sortino = RiskMetrics.calculate_sortino_ratio(returns)

    print(f"VaR (95%): {var_95:.2%}")
    print(f"CVaR (95%): {cvar_95:.2%}")
    print(f"Sortino Ratio: {sortino:.2f}")
