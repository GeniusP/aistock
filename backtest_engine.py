"""
回测引擎
执行策略回测并记录交易记录
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
import logging

from trading_strategies import BaseStrategy, Signal

logger = logging.getLogger(__name__)


class Trade:
    """交易记录类"""

    def __init__(
        self,
        symbol: str,
        entry_date: datetime,
        exit_date: Optional[datetime],
        entry_price: float,
        exit_price: Optional[float],
        quantity: int,
        trade_type: str,
        pnl: Optional[float] = None,
        pnl_pct: Optional[float] = None
    ):
        self.symbol = symbol
        self.entry_date = entry_date
        self.exit_date = exit_date
        self.entry_price = entry_price
        self.exit_price = exit_price
        self.quantity = quantity
        self.trade_type = trade_type  # 'long' or 'short'
        self.pnl = pnl
        self.pnl_pct = pnl_pct

    def __repr__(self):
        return f"Trade({self.symbol}, {self.entry_date} -> {self.exit_date}, PnL: {self.pnl:.2f})"


class Portfolio:
    """投资组合类"""

    def __init__(self, initial_capital: float, commission: float = 0.001, slippage: float = 0.0001):
        """
        初始化投资组合

        Args:
            initial_capital: 初始资金
            commission: 手续费率
            slippage: 滑点率
        """
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.positions = {}  # {symbol: quantity}
        self.trades: List[Trade] = []
        self.equity_curve = []

    def get_portfolio_value(self, current_prices: Dict[str, float]) -> float:
        """计算当前组合价值"""
        position_value = sum(
            quantity * current_prices.get(symbol, 0)
            for symbol, quantity in self.positions.items()
        )
        return self.cash + position_value

    def execute_trade(
        self,
        symbol: str,
        signal: int,
        price: float,
        date: datetime,
        current_prices: Dict[str, float]
    ):
        """
        执行交易

        Args:
            symbol: 交易标的
            signal: 交易信号 (1=买入, -1=卖出, 0=持有)
            price: 当前价格
            date: 交易日期
            current_prices: 当前所有标的价格字典
        """
        # 计算滑点后的实际价格
        if signal == Signal.BUY.value:
            actual_price = price * (1 + self.slippage)
        elif signal == Signal.SELL.value:
            actual_price = price * (1 - self.slippage)
        else:
            return

        if signal == Signal.BUY.value:
            # 买入逻辑
            max_position_value = self.get_portfolio_value(current_prices) * 0.95  # 最多使用95%的资金
            quantity = int(max_position_value / actual_price)
            cost = quantity * actual_price * (1 + self.commission)

            if quantity > 0 and self.cash >= cost:
                self.cash -= cost
                self.positions[symbol] = self.positions.get(symbol, 0) + quantity

                logger.info(f"{date.date()} 买入 {symbol}: {quantity}股 @ {actual_price:.2f}")

        elif signal == Signal.SELL.value:
            # 卖出逻辑
            if symbol in self.positions and self.positions[symbol] > 0:
                quantity = self.positions[symbol]
                proceeds = quantity * actual_price * (1 - self.commission)

                # 记录交易
                entry_trade = self._find_open_position(symbol)
                if entry_trade:
                    entry_trade.exit_date = date
                    entry_trade.exit_price = actual_price
                    pnl = (actual_price - entry_trade.entry_price) * quantity
                    pnl_pct = (actual_price - entry_trade.entry_price) / entry_trade.entry_price
                    entry_trade.pnl = pnl
                    entry_trade.pnl_pct = pnl_pct

                self.cash += proceeds
                self.positions[symbol] = 0

                logger.info(f"{date.date()} 卖出 {symbol}: {quantity}股 @ {actual_price:.2f}, PnL: {pnl if entry_trade else 0:.2f}")

    def _find_open_position(self, symbol: str) -> Optional[Trade]:
        """查找未平仓的交易"""
        for trade in reversed(self.trades):
            if trade.symbol == symbol and trade.exit_date is None:
                return trade
        return None

    def record_equity(self, date: datetime, current_prices: Dict[str, float]):
        """记录权益曲线"""
        portfolio_value = self.get_portfolio_value(current_prices)
        self.equity_curve.append({
            'date': date,
            'portfolio_value': portfolio_value,
            'cash': self.cash,
            'positions': self.positions.copy()
        })


class BacktestEngine:
    """回测引擎"""

    def __init__(
        self,
        strategy: BaseStrategy,
        initial_capital: float = 100000,
        commission: float = 0.001,
        slippage: float = 0.0001
    ):
        """
        初始化回测引擎

        Args:
            strategy: 交易策略
            initial_capital: 初始资金
            commission: 手续费率
            slippage: 滑点率
        """
        self.strategy = strategy
        self.portfolio = Portfolio(initial_capital, commission, slippage)
        self.results = {}

    def run(self, data: pd.DataFrame, symbol: str = "DEFAULT") -> Dict:
        """
        运行回测

        Args:
            data: 包含OHLCV和信号的DataFrame
            symbol: 交易标的名称

        Returns:
            回测结果字典
        """
        logger.info(f"开始回测策略: {self.strategy.name}")

        # 生成交易信号
        data_with_signals = self.strategy.generate_signals(data)

        # 确保按日期排序
        data_with_signals = data_with_signals.sort_values('datetime' if 'datetime' in data_with_signals.columns else data_with_signals.index)

        # 逐行回测
        for idx, row in data_with_signals.iterrows():
            date = row['datetime'] if 'datetime' in row else idx
            price = row['close']
            signal = row['signal']

            current_prices = {symbol: price}

            # 执行交易
            if signal != Signal.HOLD.value:
                # 如果是新买入,记录入场交易
                if signal == Signal.BUY.value:
                    trade = Trade(
                        symbol=symbol,
                        entry_date=date,
                        exit_date=None,
                        entry_price=price,
                        exit_price=None,
                        quantity=0,  # 会在execute_trade中计算
                        trade_type='long'
                    )
                    self.portfolio.trades.append(trade)

                self.portfolio.execute_trade(symbol, signal, price, date, current_prices)

            # 记录权益
            self.portfolio.record_equity(date, current_prices)

        # 计算回测结果
        self.results = self._calculate_results(data_with_signals, symbol)

        logger.info(f"回测完成. 总收益率: {self.results['total_return']:.2%}")
        return self.results

    def _calculate_results(self, data: pd.DataFrame, symbol: str) -> Dict:
        """计算回测结果指标"""

        equity_df = pd.DataFrame(self.portfolio.equity_curve)
        if equity_df.empty:
            return {}

        # 基本指标
        initial_capital = self.portfolio.initial_capital
        final_value = equity_df['portfolio_value'].iloc[-1]
        total_return = (final_value - initial_capital) / initial_capital

        # 计算日收益率
        equity_df['daily_return'] = equity_df['portfolio_value'].pct_change()

        # 夏普比率 (假设无风险利率为0)
        sharpe_ratio = np.sqrt(252) * equity_df['daily_return'].mean() / equity_df['daily_return'].std() if equity_df['daily_return'].std() != 0 else 0

        # 最大回撤
        equity_df['cummax'] = equity_df['portfolio_value'].cummax()
        equity_df['drawdown'] = (equity_df['portfolio_value'] - equity_df['cummax']) / equity_df['cummax']
        max_drawdown = equity_df['drawdown'].min()

        # 交易统计
        completed_trades = [t for t in self.portfolio.trades if t.exit_date is not None]
        winning_trades = [t for t in completed_trades if t.pnl and t.pnl > 0]
        losing_trades = [t for t in completed_trades if t.pnl and t.pnl < 0]

        win_rate = len(winning_trades) / len(completed_trades) if completed_trades else 0

        avg_win = np.mean([t.pnl for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t.pnl for t in losing_trades]) if losing_trades else 0

        profit_factor = abs(sum(t.pnl for t in winning_trades) / sum(t.pnl for t in losing_trades)) if losing_trades and sum(t.pnl for t in losing_trades) != 0 else float('inf')

        # 基准对比
        buy_hold_return = (data['close'].iloc[-1] - data['close'].iloc[0]) / data['close'].iloc[0]

        results = {
            'strategy_name': self.strategy.name,
            'initial_capital': initial_capital,
            'final_value': final_value,
            'total_return': total_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'total_trades': len(completed_trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'buy_hold_return': buy_hold_return,
            'equity_curve': equity_df,
            'trades': completed_trades
        }

        return results

    def get_trade_history(self) -> pd.DataFrame:
        """获取交易历史"""
        trades_data = []
        for trade in self.portfolio.trades:
            if trade.exit_date:
                trades_data.append({
                    'symbol': trade.symbol,
                    'entry_date': trade.entry_date,
                    'exit_date': trade.exit_date,
                    'entry_price': trade.entry_price,
                    'exit_price': trade.exit_price,
                    'quantity': trade.quantity,
                    'pnl': trade.pnl,
                    'pnl_pct': trade.pnl_pct
                })
        return pd.DataFrame(trades_data)


if __name__ == "__main__":
    # 测试代码
    from data_fetcher import DataFetcher
    from trading_strategies import MovingAverageCrossover

    # 获取数据
    fetcher = DataFetcher()
    data = fetcher.fetch_data("AAPL", period="2y")

    # 创建策略
    strategy = MovingAverageCrossover(short_window=20, long_window=50)

    # 运行回测
    engine = BacktestEngine(strategy, initial_capital=100000, commission=0.001)
    results = engine.run(data, "AAPL")

    # 打印结果
    print("\n=== 回测结果 ===")
    print(f"策略: {results['strategy_name']}")
    print(f"初始资金: ${results['initial_capital']:,.2f}")
    print(f"最终资金: ${results['final_value']:,.2f}")
    print(f"总收益率: {results['total_return']:.2%}")
    print(f"夏普比率: {results['sharpe_ratio']:.2f}")
    print(f"最大回撤: {results['max_drawdown']:.2%}")
    print(f"总交易次数: {results['total_trades']}")
    print(f"胜率: {results['win_rate']:.2%}")
    print(f"盈亏比: {results['profit_factor']:.2f}")
    print(f"买入持有收益率: {results['buy_hold_return']:.2%}")

    # 保存交易历史
    trade_history = engine.get_trade_history()
    if not trade_history.empty:
        print("\n=== 交易历史 ===")
        print(trade_history.head(10))
