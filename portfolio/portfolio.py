import numpy as np
import pandas as pd
import yfinance as yf
import datetime
from dateutil.relativedelta import relativedelta

class Portfolio:

    def __init__(self, trades_df):
        self.price_history_df = None
        self.trades_df = trades_df
        self.cash = 0
        self.raw_investment = 0
        self.holdings = {}
        self.profit = {}
        self.equity_history_df = None
        self.unit_history_df = None
        self.profit_history_df = None
        self.simulate()

    def simulate(self):
        tickers = list(self.trades_df["ticker"].unique())
        start_date = self.trades_df.index[0]
        end_date = self.trades_df.index[-1]

        self.price_history_df = yf.download(
            tickers,
            start=start_date,
            end=end_date,
            group_by="ticker",
            interval="1d"
        )

        self.price_history_df.index = self.price_history_df.index.date

        unit_history = []
        equity_history = []
        profit_history = []
        date_range = pd.date_range(
            start=start_date,
            end=end_date
        )

        for d in date_range:
            day = d.date()

            skip_flag = False
            try:
                df_day = self.trades_df.loc[[day]]
            except KeyError:
                # no trades found on day, skip
                skip_flag = True

            if not skip_flag:
                for index, row in df_day.iterrows():
                    error_code = self.trade_stock(
                        row["action"],
                        row["ticker"],
                        units=row["units"],
                        settlement=row["settlement"]
                    )

                    if error_code:
                        print(f"Invalid trade occured on {day}")
            
            profit_history.append(self.profit.copy())
            unit_history.append(self.holdings.copy())
            equity_history.append(self.equity_on(day))

        self.unit_history_df = pd.DataFrame(unit_history, index=date_range)
        self.unit_history_df.reindex(sorted(self.unit_history_df.columns), axis=1)

        self.equity_history_df = pd.DataFrame(equity_history, index=date_range)
        self.equity_history_df.dropna(how="all", inplace=True)
        
        self.profit_history_df = pd.DataFrame(profit_history, index=date_range)
        self.profit_history_df = self.profit_history_df.add(self.equity_history_df)
        self.profit_history_df.dropna(how="all", inplace=True)
        self.profit_history_df.reindex(sorted(self.profit_history_df.columns), axis=1)

    def equity_on(self, date_obj):
        equity = {}
        for ticker, units in self.holdings.items():
            try:
                ticker_price_history_df = self.price_history_df[ticker]
            except KeyError:
                print(f"Price history for {ticker} not found")
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

    def trade_stock(self, action, ticker, units, settlement):
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

        #self.print_holdings()

    def print_holdings(self):
        print(16*"=")

        print(f"cash: {self.cash}")

        for ticker, units in self.holdings.items():
            if units == 0:
                continue

            print(f"{ticker}: {int(units)}")

        print(16*"=")
        print()
