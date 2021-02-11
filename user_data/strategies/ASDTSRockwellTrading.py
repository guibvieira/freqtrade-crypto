
# --- Do not remove these libs ---
from freqtrade.strategy.interface import IStrategy
from typing import Dict, List
from functools import reduce
from pandas import DataFrame
# --------------------------------

import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib


class ASDTSRockwellTrading(IStrategy):
    """
    trading strategy based on the concept explained at https://www.youtube.com/watch?v=mmAWVmKN4J0
    author@: Gert Wohlgemuth

    idea:

        uptrend definition:
            MACD above 0 line AND above MACD signal


        downtrend definition:
            MACD below 0 line and below MACD signal

        sell definition:
            MACD below MACD signal

    it's basically a very simple MACD based strategy and we ignore the definition of the entry and exit points in this case, since the trading bot, will take of this already

    """

    # Minimal ROI designed for the strategy.
    # This attribute will be overridden if the config file contains "minimal_roi"
    
    # Original Settings
    # minimal_roi = {
    #     "60":  0.01,
    #     "30":  0.03,
    #     "20":  0.04,
    #     "0":  0.05
    # }

    minimal_roi = {
        "214":  0,
        "136":  0.0316,
        "42":  0.102,
        "0":  0.10
    }

    

    # Optimal stoploss designed for the strategy
    # This attribute will be overridden if the config file contains "stoploss"
    stoploss = -0.05

    # Optimal ticker interval for the strategy
    ticker_interval = '5m'

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        macd = ta.MACD(dataframe)
        dataframe['macd'] = macd['macd']
        dataframe['macdsignal'] = macd['macdsignal']
        dataframe['macdhist'] = macd['macdhist']

        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the buy signal for the given dataframe
        :param dataframe: DataFrame
        :return: DataFrame with buy column
        """
        dataframe.loc[
            (
                (dataframe['macd'] > 0) &
                (dataframe['macd'] > dataframe['macdsignal'])
            ),
            'buy'] = 1

        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the sell signal for the given dataframe
        :param dataframe: DataFrame
        :return: DataFrame with buy column
        """
        dataframe.loc[
            (
                (dataframe['macd'] < dataframe['macdsignal'])
            ),
            'sell'] = 1
        return dataframe
