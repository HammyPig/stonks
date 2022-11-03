import numpy as np
import pandas as pd

class BrokerParser:

    REQUIRED_COLUMNS = ["date", "action", "units", "ticker", "settlement"]

    def parse_commsec(filepath):
        commsec_trades_df = pd.read_csv(filepath)
        commsec_trades_df.rename(columns={
            "Date": "date",
        }, inplace=True)

        commsec_trades_df["date"] = pd.to_datetime(commsec_trades_df["date"], format="%d/%m/%Y")

        # filter to only include trades
        commsec_trades_df = commsec_trades_df.loc[
            (commsec_trades_df["Details"].str[0] == "B") | 
            (commsec_trades_df["Details"].str[0] == "S")
        ]

        # split details column into seperate columns
        commsec_trades_df["action"] = commsec_trades_df.apply(lambda x: "buy" if x["Details"][0] == "B" else "sell", axis=1)
        commsec_trades_df["units"] = commsec_trades_df.apply(lambda x: x["Details"].split(" ")[1], axis=1)
        commsec_trades_df["ticker"] = commsec_trades_df.apply(lambda x: x["Details"].split(" ")[2], axis=1)
        commsec_trades_df["settlement"] = commsec_trades_df["Debit($)"]
        commsec_trades_df["settlement"].fillna(commsec_trades_df["Credit($)"], inplace=True)

        # filter to only required columns
        commsec_trades_df.drop(commsec_trades_df.columns.difference(BrokerParser.REQUIRED_COLUMNS), axis=1, inplace=True)

        # original file is in reverse order
        commsec_trades_df = commsec_trades_df[::-1]

        commsec_trades_df["ticker"] += ".AX"
        commsec_trades_df.set_index("date", inplace=True)
        commsec_trades_df["units"] = commsec_trades_df["units"].astype("int")

        return commsec_trades_df

    def parse_stake(filepath):
        stake_trades_df = pd.read_excel(filepath, sheet_name="Trades")
        stake_trades_df.rename(columns={
            "DATE": "date",
            "SIDE": "action",
            "UNITS": "units",
            "SYMBOL": "ticker",
            "NET AMOUNT": "settlement"
        }, inplace=True)

        stake_trades_df["date"] = pd.to_datetime(stake_trades_df["date"], format="%d-%m-%Y")
        stake_trades_df["action"] = stake_trades_df["action"].str.lower()
        stake_trades_df.drop(stake_trades_df.columns.difference(BrokerParser.REQUIRED_COLUMNS), axis=1, inplace=True)

        # original file is in reverse order
        stake_trades_df = stake_trades_df[::-1]

        stake_trades_df["ticker"] += ".AX"
        stake_trades_df.set_index("date", inplace=True)

        stake_trades_df["settlement"] = np.abs(stake_trades_df["settlement"])

        return stake_trades_df
