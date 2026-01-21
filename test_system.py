"""
系统测试脚本
测试各个模块的基本功能
"""

import sys


def test_data_fetcher():
    """测试数据获取模块"""
    print("\n" + "=" * 80)
    print("测试数据获取模块")
    print("=" * 80)

    try:
        from data_fetcher import DataFetcher

        fetcher = DataFetcher()
        data = fetcher.fetch_data("AAPL", period="3mo")

        if not data.empty:
            print(f"✓ 成功获取数据: {len(data)} 条记录")
            print(f"  列: {list(data.columns)[:5]}...")
            return True
        else:
            print("✗ 数据为空")
            return False

    except Exception as e:
        print(f"✗ 错误: {str(e)}")
        return False


def test_technical_indicators():
    """测试技术指标模块"""
    print("\n" + "=" * 80)
    print("测试技术指标模块")
    print("=" * 80)

    try:
        from data_fetcher import DataFetcher
        from technical_indicators import TechnicalIndicators

        fetcher = DataFetcher()
        data = fetcher.fetch_data("AAPL", period="3mo")

        data_with_indicators = TechnicalIndicators.add_all_indicators(data)

        print(f"✓ 成功添加技术指标")
        print(f"  原始列数: {len(data.columns)}")
        print(f"  新列数: {len(data_with_indicators.columns)}")
        print(f"  添加的指标数: {len(data_with_indicators.columns) - len(data.columns)}")

        return True

    except Exception as e:
        print(f"✗ 错误: {str(e)}")
        return False


def test_trading_strategies():
    """测试交易策略模块"""
    print("\n" + "=" * 80)
    print("测试交易策略模块")
    print("=" * 80)

    try:
        from data_fetcher import DataFetcher
        from trading_strategies import MovingAverageCrossover, MACDStrategy

        fetcher = DataFetcher()
        data = fetcher.fetch_data("AAPL", period="1y")

        # 测试MA交叉策略
        strategy1 = MovingAverageCrossover(20, 50)
        result1 = strategy1.generate_signals(data)
        signals1 = result1['signal'].value_counts()
        print(f"✓ MA交叉策略 - 买入: {signals1.get(1, 0)}, 卖出: {signals1.get(-1, 0)}")

        # 测试MACD策略
        strategy2 = MACDStrategy()
        result2 = strategy2.generate_signals(data)
        signals2 = result2['signal'].value_counts()
        print(f"✓ MACD策略 - 买入: {signals2.get(1, 0)}, 卖出: {signals2.get(-1, 0)}")

        return True

    except Exception as e:
        print(f"✗ 错误: {str(e)}")
        return False


def test_backtest_engine():
    """测试回测引擎"""
    print("\n" + "=" * 80)
    print("测试回测引擎")
    print("=" * 80)

    try:
        from data_fetcher import DataFetcher
        from trading_strategies import MovingAverageCrossover
        from backtest_engine import BacktestEngine

        fetcher = DataFetcher()
        data = fetcher.fetch_data("AAPL", period="1y")

        strategy = MovingAverageCrossover(20, 50)
        engine = BacktestEngine(strategy, initial_capital=100000)
        results = engine.run(data, "AAPL")

        print(f"✓ 回测完成")
        print(f"  初始资金: ${results['initial_capital']:,.2f}")
        print(f"  最终资金: ${results['final_value']:,.2f}")
        print(f"  总收益率: {results['total_return']:.2%}")
        print(f"  夏普比率: {results['sharpe_ratio']:.2f}")
        print(f"  最大回撤: {results['max_drawdown']:.2%}")
        print(f"  交易次数: {results['total_trades']}")

        return True

    except Exception as e:
        print(f"✗ 错误: {str(e)}")
        return False


def test_risk_management():
    """测试风险管理模块"""
    print("\n" + "=" * 80)
    print("测试风险管理模块")
    print("=" * 80)

    try:
        from risk_management import (
            FixedRatioSizer, KellyCriterionSizer,
            ATRBasedSizer, RiskManager
        )

        portfolio_value = 100000
        entry_price = 150

        # 测试固定比例仓位管理
        sizer1 = FixedRatioSizer(0.2)
        size1 = sizer1.calculate_position_size(portfolio_value, entry_price)
        print(f"✓ 固定比例法: {size1} 股")

        # 测试凯利公式
        sizer2 = KellyCriterionSizer(0.55, 0.05, 0.03)
        size2 = sizer2.calculate_position_size(portfolio_value, entry_price)
        print(f"✓ 凯利公式: {size2} 股")

        # 测试ATR法
        sizer3 = ATRBasedSizer(2.0, 0.02)
        size3 = sizer3.calculate_position_size(
            portfolio_value, entry_price, atr=5.0
        )
        print(f"✓ ATR法: {size3} 股")

        # 测试风险管理器
        rm = RiskManager(max_position_size=0.2)
        allowed, reason = rm.check_entry_conditions("AAPL", 15000, 100000)
        print(f"✓ 风险检查: {allowed} - {reason}")

        return True

    except Exception as e:
        print(f"✗ 错误: {str(e)}")
        return False


def main():
    """运行所有测试"""
    print("=" * 80)
    print("量化交易系统 - 功能测试")
    print("=" * 80)

    tests = [
        ("数据获取模块", test_data_fetcher),
        ("技术指标模块", test_technical_indicators),
        ("交易策略模块", test_trading_strategies),
        ("回测引擎", test_backtest_engine),
        ("风险管理模块", test_risk_management),
    ]

    results = []

    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n✗ {name} 测试失败: {str(e)}")
            results.append((name, False))

    # 打印测试总结
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for name, success in results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"{name:20s}: {status}")

    print(f"\n总计: {passed}/{total} 测试通过")

    if passed == total:
        print("\n🎉 所有测试通过!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
