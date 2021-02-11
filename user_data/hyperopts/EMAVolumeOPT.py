# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement

import talib.abstract as ta
from pandas import DataFrame
from typing import Dict, Any, Callable, List
from functools import reduce

from skopt.space import Categorical, Dimension, Integer, Real

import freqtrade.vendor.qtpylib.indicators as qtpylib
from freqtrade.optimize.hyperopt_interface import IHyperOpt

class_name = 'EMAVolumeOPT'


class EMAVolumeOPT(IHyperOpt):
    """
    Default hyperopt provided by freqtrade bot.
    You can override it with your own hyperopt
    """

    @staticmethod
    def populate_indicators(dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['ema50']=ta.EMA(dataframe, timeperiod=50)
        dataframe['ema200']=ta.EMA(dataframe, timeperiod=200)

        # dataframe['ema5']=ta.EMA(dataframe, timeperiod=5)
        # dataframe['ema10']=ta.EMA(dataframe, timeperiod=10)
        
        dataframe['ema13']=ta.EMA(dataframe, timeperiod=13)
        dataframe['ema34']=ta.EMA(dataframe, timeperiod=34)
        dataframe['ema7']=ta.EMA(dataframe, timeperiod=7)
        dataframe['ema21']=ta.EMA(dataframe, timeperiod=21)
        dataframe['volume-mean'] = dataframe['volume'].rolling(window=10).mean()

        # RSI
        dataframe['rsi'] = ta.RSI(dataframe)
        dataframe['sell-rsi'] = ta.RSI(dataframe)
        
        return dataframe

    @staticmethod
    def buy_strategy_generator(params: Dict[str, Any]) -> Callable:
        """
        Define the buy strategy parameters to be used by hyperopt
        """
        def populate_buy_trend(dataframe: DataFrame, metadata: dict) -> DataFrame:
            """
            Buy strategy Hyperopt will build and use
            """
            conditions = []
            # GUARDS AND TRENDS
            if 'volume-enabled' in params and params['volume-enabled']:
                conditions.append(dataframe['volume'] > dataframe['volume'].rolling(window=params['volume-window']).mean())
            if 'ema_7_21-enabled' in params and params['ema_7_21-enabled']:
                conditions.append(qtpylib.crossed_above(dataframe['ema13'], dataframe['ema34']))
            if 'ema_13_34-enabled' in params and params['ema_13_34-enabled']:
                conditions.append(qtpylib.crossed_above(dataframe['ema13'], dataframe['ema34']))
            if 'ema_50_200-enabled' in params and params['ema_50_200-enabled']:
                conditions.append(qtpylib.crossed_above(dataframe['ema50'], dataframe['ema200']))
                

            # TRIGGERS
            if 'trigger' in params:
                if params['trigger'] == 'volume':
                    conditions.append(dataframe['volume'] > dataframe['volume-mean'])
                if params['trigger'] == 'ema_7_21_crossover':
                    conditions.append(qtpylib.crossed_above(dataframe['ema7'], dataframe['ema21']))

                if params['trigger'] == 'ema_13_34_crossover':
                    conditions.append(qtpylib.crossed_above(dataframe['ema13'], dataframe['ema34']))

                if params['trigger'] == 'ema_50_200_crossover':
                    conditions.append(qtpylib.crossed_above(dataframe['ema50'], dataframe['ema200']))


            dataframe.loc[
                reduce(lambda x, y: x & y, conditions),
                'buy'] = 1

            return dataframe

        return populate_buy_trend

    @staticmethod
    def indicator_space() -> List[Dimension]:
        """
        Define your Hyperopt space for searching strategy parameters
        categorical -> try enabling and disabling these parameters doing the search 
        """
        return [
            Integer(5, 30, name='volume-window'),
            Categorical([True, False], name='volume-enabled'),
            Categorical([True, False], name='ema_7_21-enabled'),
            Categorical([True, False], name='ema_13_34-enabled'),
            Categorical([True, False], name='ema_50_200-enabled'),
            Categorical(['volume', 'ema_7_21_crossover', 'ema_13_34_crossover', 'ema_50_200_crossover'], name='trigger')
        ]

    @staticmethod
    def sell_strategy_generator(params: Dict[str, Any]) -> Callable:
        """
        Define the sell strategy parameters to be used by hyperopt
        """
        def populate_sell_trend(dataframe: DataFrame, metadata: dict) -> DataFrame:
            """
            Sell strategy Hyperopt will build and use
            """
            # print(params)
            conditions = []
            # GUARDS AND TRENDS
            if 'sell-rsi-enabled' in params and params['sell-rsi-enabled']:
                conditions.append(dataframe['rsi'] > params['sell-rsi-value'])

            # TRIGGERS
            if 'sell-trigger' in params:
                if params['sell-trigger'] == 'sell-ema_7_21':
                    conditions.append(qtpylib.crossed_above(dataframe['ema7'], dataframe['ema21']))
                if params['sell-trigger'] == 'sell-ema_13_34':
                    conditions.append(qtpylib.crossed_below(dataframe['ema13'], dataframe['ema34']))
                if params['sell-trigger'] == 'sell-ema_50_200':
                    conditions.append(qtpylib.crossed_below(dataframe['ema50'], dataframe['ema200']))

            dataframe.loc[
                reduce(lambda x, y: x & y, conditions),
                'sell'] = 1

            return dataframe

        return populate_sell_trend

    @staticmethod
    def sell_indicator_space() -> List[Dimension]:
        """
        Define your Hyperopt space for searching sell strategy parameters
        """
        return [
            Integer(30, 100, name='sell-rsi-value'),
            Categorical([True, False], name='sell-rsi-enabled'),
            Categorical(['sell-ema_7_21',
                         'sell-ema_13_34',
                         'sell-ema_50_200'], name='sell-trigger')
        ]

    @staticmethod
    def generate_roi_table(params: Dict) -> Dict[int, float]:
        """
        Generate the ROI table that will be used by Hyperopt
        """
        roi_table = {}
        roi_table[0] = params['roi_p1'] + params['roi_p2'] + params['roi_p3']
        roi_table[params['roi_t3']] = params['roi_p1'] + params['roi_p2']
        roi_table[params['roi_t3'] + params['roi_t2']] = params['roi_p1']
        roi_table[params['roi_t3'] + params['roi_t2'] + params['roi_t1']] = 0

        return roi_table

    @staticmethod
    def stoploss_space() -> List[Dimension]:
        """
        Stoploss Value to search
        """
        return [
            Real(-0.5, -0.02, name='stoploss'),
        ]

    @staticmethod
    def roi_space() -> List[Dimension]:
        """
        Values to search for each ROI steps
        """
        return [
            Integer(10, 120, name='roi_t1'),
            Integer(10, 60, name='roi_t2'),
            Integer(10, 40, name='roi_t3'),
            Real(0.01, 0.04, name='roi_p1'),
            Real(0.01, 0.07, name='roi_p2'),
            Real(0.01, 0.20, name='roi_p3'),
        ]

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the buy signal for the given dataframe
        :param dataframe: DataFrame
        :return: DataFrame with buy column
        """
        dataframe.loc[
            (
                (qtpylib.crossed_above(dataframe['ema13'], dataframe['ema34'])) &
                (dataframe['volume'] > dataframe['volume'].rolling(window=10).mean())
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
                (qtpylib.crossed_below(dataframe['ema13'], dataframe['ema34']))
            ),
            'sell'] = 1
        return dataframe