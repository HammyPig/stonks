import datetime
import pandas as pd
from portfolio import Portfolio

trades1 = [
    [datetime.date(2020, 3, 23), "buy", "WBC.AX", 70, 997],
    [datetime.date(2022, 3, 23), "sell", "WBC.AX", 70, 1646.05]
]

trades1 = pd.DataFrame(trades1, columns=["date", "action", "ticker", "units", "settlement"])
trades1.set_index("date", inplace=True)

trades2 = [
    [datetime.date(2020, 2, 21), "buy", "VGS.AX", 11, 980.64],
    [datetime.date(2020, 3, 23), "buy", "WBC.AX", 70, 997],
    [datetime.date(2022, 1, 4), "sell", "VGS.AX", 11, 1167.39],
    [datetime.date(2022, 3, 23), "sell", "WBC.AX", 70, 1646.05]
]

trades2 = pd.DataFrame(trades2, columns=["date", "action", "ticker", "units", "settlement"])
trades2.set_index("date", inplace=True)

def test_get_trades():
    p = Portfolio(trades1)
    assert p.get_trades().equals(trades1)

def test_set_trades():
    p = Portfolio(trades1)
    p.set_trades(trades2)
    assert p.get_trades().equals(trades2)

def test_unit_history1():
    p = Portfolio(trades1)
    assert p.unit_history().loc["2020-03-23"]["WBC.AX"] == 70
    assert p.unit_history().loc["2020-03-24"]["WBC.AX"] == 70

    assert p.unit_history().loc["2022-03-22"]["WBC.AX"] == 70
    assert p.unit_history().loc["2022-03-23"]["WBC.AX"] == 0

def test_unit_history2():
    p = Portfolio(trades2)
    assert p.unit_history().loc["2020-02-21"]["VGS.AX"] == 11
    assert p.unit_history().loc["2020-02-22"]["VGS.AX"] == 11

    assert p.unit_history().loc["2022-01-03"]["VGS.AX"] == 11
    assert p.unit_history().loc["2022-01-04"]["VGS.AX"] == 0
    assert p.unit_history().loc["2022-01-05"]["VGS.AX"] == 0
    
    assert pd.isna(p.unit_history().loc["2020-03-22"]["WBC.AX"])
    assert p.unit_history().loc["2020-03-23"]["WBC.AX"] == 70
    assert p.unit_history().loc["2020-03-24"]["WBC.AX"] == 70

    assert p.unit_history().loc["2022-03-22"]["WBC.AX"] == 70
    assert p.unit_history().loc["2022-03-23"]["WBC.AX"] == 0

def test_equity_history1():
    p = Portfolio(trades1)
    assert round(p.equity_history().loc["2020-03-23"]["WBC.AX"], 2) == 987
    assert round(p.equity_history().loc["2020-10-28"]["WBC.AX"], 2) == 1281.7
    assert round(p.equity_history().loc["2021-05-24"]["WBC.AX"], 2) == 1818.6
    assert round(p.equity_history().loc["2021-09-20"]["WBC.AX"], 2) == 1771
    assert p.equity_history().loc["2022-03-23"]["WBC.AX"] == 0

def test_equity_history2():
    p = Portfolio(trades2)
    assert round(p.equity_history().loc["2020-03-23"]["WBC.AX"], 2) == 987
    assert round(p.equity_history().loc["2020-10-28"]["WBC.AX"], 2) == 1281.7
    assert round(p.equity_history().loc["2021-05-24"]["WBC.AX"], 2) == 1818.6
    assert round(p.equity_history().loc["2021-09-20"]["WBC.AX"], 2) == 1771
    assert p.equity_history().loc["2022-03-23"]["WBC.AX"] == 0

    assert round(p.equity_history().loc["2020-03-23"]["VGS.AX"], 2) == 743.6
    assert round(p.equity_history().loc["2020-10-28"]["VGS.AX"], 2) == 876.59
    assert round(p.equity_history().loc["2021-05-24"]["VGS.AX"], 2) == 1008.81
    assert round(p.equity_history().loc["2021-09-20"]["VGS.AX"], 2) == 1118.81
    assert p.equity_history().loc["2022-01-04"]["VGS.AX"] == 0
    assert p.equity_history().loc["2022-03-23"]["VGS.AX"] == 0

def test_profit_history1():
    p = Portfolio(trades1)
    assert round(p.profit_history().loc["2020-03-23"])["WBC.AX"] == 987 - 997
    assert round(p.profit_history().loc["2020-10-28"]["WBC.AX"], 2) == round((1281.7 - 997), 2)
    assert round(p.profit_history().loc["2021-05-24"]["WBC.AX"], 2) == round((1818.6 - 997), 2)
    assert round(p.profit_history().loc["2021-09-20"]["WBC.AX"], 2) == round((1771 - 997), 2)
    assert p.profit_history().loc["2022-03-23"]["WBC.AX"] == round((1666 - 19.95 - 997), 2)

def test_profit_history2():
    p = Portfolio(trades2)
    print(p.profit_history().tail(60))
    assert round(p.profit_history().loc["2020-03-23"])["WBC.AX"] == 987 - 997
    assert round(p.profit_history().loc["2020-10-28"]["WBC.AX"], 2) == round((1281.7 - 997), 2)
    assert round(p.profit_history().loc["2021-05-24"]["WBC.AX"], 2) == round((1818.6 - 997), 2)
    assert round(p.profit_history().loc["2021-09-20"]["WBC.AX"], 2) == round((1771 - 997), 2)
    assert round(p.profit_history().loc["2022-03-23"]["WBC.AX"], 2) == round((1666 - 19.95 - 997), 2)

    assert round(p.profit_history().loc["2020-02-21"])["VGS.AX"] == 970.64 - 980.64
    assert round(p.profit_history().loc["2020-10-28"]["VGS.AX"], 2) == round((876.59 - 980.64), 2)
    assert round(p.profit_history().loc["2021-05-24"]["VGS.AX"], 2) == round((1008.81 - 980.64), 2)
    assert round(p.profit_history().loc["2021-09-20"]["VGS.AX"], 2) == round((1118.81 - 980.64), 2)
    assert round(p.profit_history().loc["2022-03-23"]["VGS.AX"], 2) == round((1167.39 - 980.64), 2)

def test_cost():
    p = Portfolio(trades1)
    assert round(p.cost(), 2) == 997

def test_cost2():
    p = Portfolio(trades2)
    assert round(p.cost(), 2) == 1977.64
