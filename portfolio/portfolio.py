import numpy as np
import pandas as pd
import yfinance as yf
import datetime
from dateutil.relativedelta import relativedelta

class Portfolio:

    def __init__(self, trades_df):
        self.price_history_df = None
        self.set_trades(trades_df)

    def _price_history(self):
        tickers = list(self.trades_df["ticker"].unique())

        price_history_df = yf.download(
            tickers,
            start=self.trades_df.index[0],
            end=self.trades_df.index[-1] + datetime.timedelta(days=1),
            group_by="ticker",
            interval="1d"
        )

        price_history_df.index = price_history_df.index.date
        return price_history_df

    def _trade_stock(self, action, ticker, units, settlement):
        if ticker not in self.holdings:
            self.holdings[ticker] = 0
            self.profit[ticker] = 0

        if action == "buy":
            self.profit[ticker] -= settlement
            self.cash -= settlement
            self.holdings[ticker] += units

            if self.cash < 0:
                self.raw_investment += -self.cash
                self.cash = 0

        elif action == "sell":
            self.profit[ticker] += settlement
            self.cash += settlement
            self.holdings[ticker] -= units

            if self.holdings[ticker] < 0:
                print(f"Invalid trade occurred for {ticker}. Attempted to sell {units} for {settlement} resulting in {self.holdings[ticker]}")
                return 1

        elif action == "dividend":
            #if not pd.isna(settlement):
            #    self.cash += settlement

            if not pd.isna(units):
                self.holdings[ticker] += units

        return 0

    def _execute_trades_on(self, day):
        try:
            df_day = self.trades_df.loc[[day]]
        except KeyError:
            # no trades found on day
            return

        for index, row in df_day.iterrows():
            error_code = self._trade_stock(
                row["action"],
                row["ticker"],
                units=row["units"],
                settlement=row["settlement"]
            )

            if error_code:
                print(f"Invalid trade occured on {day}")

    def _equity_on(self, date_obj):
        equity = {}
        for ticker, units in self.holdings.items():
            if len(list(self.trades_df["ticker"].unique())) == 1:
                ticker_price_history_df = self.price_history_df
            else:
                try:
                    ticker_price_history_df = self.price_history_df[ticker]
                except KeyError:
                    print(f"Price history for {ticker} not found")
                    #print(self.price_history_df)
                    continue
            
            try:
                unit_price = ticker_price_history_df.loc[date_obj]["Close"]
            except KeyError:
                #print(f"Price for {ticker} on day {date_obj} not found")
                continue

            equity[ticker] = units * unit_price
        
        if not equity:
            return {}

        equity["CASH"] = self.cash

        return equity

    def _simulate(self):
        unit_history = []
        equity_history = []
        profit_history = []
        
        date_range = pd.date_range(
            start=self.trades_df.index[0],
            end=self.trades_df.index[-1]
        )

        for day in date_range:
            day = day.date()
            self._execute_trades_on(day)
            
            unit_history.append(self.holdings.copy())
            equity_history.append(self._equity_on(day))
            profit_history.append(self.profit.copy())

        self.unit_history_df = pd.DataFrame(unit_history, index=date_range)
        self.unit_history_df.reindex(sorted(self.unit_history_df.columns), axis=1)

        self.equity_history_df = pd.DataFrame(equity_history, index=date_range)
        self.equity_history_df.dropna(how="all", inplace=True)
        
        self.profit_history_df = pd.DataFrame(profit_history, index=date_range)
        self.profit_history_df = self.profit_history_df.add(self.equity_history_df)
        self.profit_history_df.dropna(how="all", inplace=True)
        self.profit_history_df.reindex(sorted(self.profit_history_df.columns), axis=1)

    def get_trades(self):
        return self.trades_df

    def set_trades(self, trades):
        self.trades_df = trades
        self.cash = 0
        self.raw_investment = 0
        self.holdings = {}
        self.profit = {}
        self.price_history_df = self._price_history()
        self.equity_history_df = None
        self.unit_history_df = None
        self.profit_history_df = None
        self._simulate()

    def unit_history(self):
        return self.unit_history_df

    def equity_history(self):
        return self.equity_history_df

    def profit_history(self):
        return self.profit_history_df

    def cost(self):
        return self.raw_investment

