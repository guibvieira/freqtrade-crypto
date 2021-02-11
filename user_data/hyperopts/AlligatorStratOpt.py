# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement

import talib.abstract as ta
from pandas import DataFrame
from typing import Dict, Any, Callable, List
from functools import reduce

from skopt.space import Categorical, Dimension, Integer, Real

import freqtrade.vendor.qtpylib.indicators as qtpylib
from freqtrade.optimize.hyperopt_interface import IHyperOpt

class_name = 'AlligatorStrat_OPT'


class AlligatorStrat_OPT(IHyperOpt):
    """
    Default hyperopt provided by freqtrade bot.
    You can override it with your own hyperopt
    """

    @staticmethod
    def populate_indicators(dataframe: DataFrame, metadata: dict) -> DataFrame:
        
        dataframe['SMAShort'] = ta.SMA(dataframe, timeperiod=5)
        dataframe['SMAMedium'] = ta.SMA(dataframe, timeperiod=8)
        dataframe['SMALong'] = ta.SMA(dataframe, timeperiod=13)

        macd = ta.MACD(dataframe)
        dataframe['macd'] = macd['macd']
        dataframe['macdsignal'] = macd['macdsignal']
        dataframe['macdhist'] = macd['macdhist']
        
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
            if 'macd-enabled' in params and params['macd-enabled']:
                conditions.append(dataframe['macd'] > 0)
            if 'macd-signal-enabled' in params and params['macd-signal-enabled']:
                conditions.append(dataframe['macd'] > dataframe['macdsignal'])
           

            #TRIGGERS
            if 'trigger' in params:
                if params['trigger'] == 'opening_jaw':
                    conditions.append(qtpylib.crossed_above(dataframe['SMAShort'], dataframe['SMAMedium']))
            
            if conditions:
                dataframe.loc[
                    reduce(lambda x, y: x & y, conditions),
                    'sell'] = 1

            return dataframe

        return populate_buy_trend

    @staticmethod
    def indicator_space() -> List[Dimension]:
        """
        Define your Hyperopt space for searching strategy parameters
        categorical -> try enabling and disabling these parameters doing the search 
        """
        return [
            Categorical([True, False], name='macd-enabled'),
            Categorical([True, False], name='macd-signal-enabled'),
            Categorical(['opening_jaw'], name='trigger')
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
            #GUARDS AND TRENDS
            if 'sell-macd-enabled' in params and params['sell-macd-enabled']:
                conditions.append((dataframe['macd'] < dataframe['macdsignal']))

            # TRIGGERS
            if 'sell-trigger' in params:
                if params['sell-trigger'] == 'closing_jaw':
                    conditions.append((dataframe['close'] < dataframe['SMAMedium']))

            if conditions:
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
            Categorical([True, False], name='sell-macd-enabled'),
            Categorical(['closing_jaw'], name='sell-trigger')
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
            Real(-0.5, -0.005, name='stoploss'),
        ]

    @staticmethod
    def roi_space() -> List[Dimension]:
        """
        Values to search for each ROI steps
        """
        return [
            Integer(0, 120, name='roi_t1'),
            Integer(0, 100, name='roi_t2'),
            Integer(10, 100, name='roi_t3'),
            Real(0.01, 0.04, name='roi_p1'),
            Real(0.01, 0.08, name='roi_p2'),
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
                #or cross above SMALong to be more conservative
                qtpylib.crossed_above(dataframe['SMAShort'], dataframe['SMAMedium']) &
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
                # qtpylib.crossed_below(dataframe['SMAShort'], dataframe['SMALong']) & 
                (dataframe['close'] < dataframe['SMAMedium']) &
                (dataframe['macd'] < dataframe['macdsignal']) 
                # qtpylib.crossed_below(dataframe['macd'], dataframe['macdsignal']) &
                # (dataframe['cci'] >= 100.0)
            ),
            'sell'] = 1
        return dataframe
