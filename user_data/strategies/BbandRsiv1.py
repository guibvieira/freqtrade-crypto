# --- Do not remove these libs ---
from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib


# --------------------------------


class BbandRsiv1(IStrategy):
    """

    author@: Gert Wohlgemuth

    converted from:

    https://github.com/sthewissen/Mynt/blob/master/src/Mynt.Core/Strategies/BbandRsi.cs

    """

    # Minimal ROI designed for the strategy.
    # adjust based on market conditions. We would recommend to keep it low for quick turn arounds
    # This attribute will be overridden if the config file contains "minimal_roi"
    # minimal_roi = {
    #     "0": 0.09187,
    #     "10": 0.0757,
    #     "34": 0.01426, 
    #     "145": 0
    # }
    
    #Only provides roi returns, but quite a safe option
    # minimal_roi = {
    #     "0": 0.07833,
    #     "35": 0.03924, 
    #     "45": 0.01344,
    #     "161": 0
    # }
    minimal_roi = {
        "0": 0.08918,
        "23": 0.03568, 
        "41": 0.01023,
        "102": 0
    }
    

    # Optimal stoploss designed for the strategy
    stoploss = -0.36899

    # Optimal ticker interval for the strategy
    ticker_interval = '1h'

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)

        bollinger = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=1)
        dataframe['bb_lowerband'] = bollinger['lower']
        dataframe['bb_middleband'] = bollinger['mid']
        dataframe['bb_upperband'] = bollinger['upper']
        # Bollinger bands
        bollinger2 = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=2)
        dataframe['bb_lowerband2'] = bollinger2['lower']
        dataframe['bb_middleband2'] = bollinger2['mid']
        dataframe['bb_upperband2'] = bollinger2['upper']

        # Bollinger bands
        bollinger3 = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=3)
        dataframe['bb_lowerband3'] = bollinger3['lower']
        dataframe['bb_middleband3'] = bollinger3['mid']
        dataframe['bb_upperband3'] = bollinger3['upper']

        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                    (dataframe['rsi'] < 20) &
                    # (dataframe['close'].shift(1) < dataframe['bb_lowerband2']) &
                    # (dataframe['close'] > dataframe['bb_lowerband2'])
                    # (dataframe['close'] > dataframe['bb_lowerband']) &
                    (qtpylib.crossed_above(dataframe['close'], dataframe['bb_lowerband2'] ))

            ),
            'buy'] = 1
        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                    (dataframe['rsi'] > 70) &
                    (dataframe['close'] > dataframe['bb_upperband'])

            ),
            'sell'] = 1
        return dataframe
 