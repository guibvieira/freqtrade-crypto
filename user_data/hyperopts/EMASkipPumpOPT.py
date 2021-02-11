# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement

from typing import Dict, Any, Callable, List
from functools import reduce
import talib.abstract as ta
from pandas import DataFrame


from skopt.space import Categorical, Dimension, Integer, Real

import freqtrade.vendor.qtpylib.indicators as qtpylib
from freqtrade.optimize.hyperopt_interface import IHyperOpt

class_name = 'EMASkipPumpOPT'

class EMASkipPumpOPT(IHyperOpt):
    """
    Default hyperopt provided by freqtrade bot.
    You can override it with your own hyperopt
    """
    EMA_SHORT_TERM = 5
    EMA_MEDIUM_TERM = 12
    EMA_LONG_TERM = 21

    ticker_interval = '5m'

    @staticmethod
    def populate_indicators(dataframe: DataFrame, metadata: dict) -> DataFrame:
        EMA_SHORT_TERM = 5
        EMA_MEDIUM_TERM = 12
        EMA_LONG_TERM = 21
        dataframe['ema_{}'.format(EMA_SHORT_TERM)] = ta.EMA(
            dataframe, timeperiod=EMA_SHORT_TERM
        )
        dataframe['ema_{}'.format(EMA_MEDIUM_TERM)] = ta.EMA(
            dataframe, timeperiod=EMA_MEDIUM_TERM
        )
        dataframe['ema_{}'.format(EMA_LONG_TERM)] = ta.EMA(
            dataframe, timeperiod=EMA_LONG_TERM
        )

        bollinger2 = qtpylib.bollinger_bands(
            qtpylib.typical_price(dataframe), window=20, stds=2
        )
        dataframe['bb_lowerband2'] = bollinger2['lower']
        dataframe['bb_middleband2'] = bollinger2['mid']
        dataframe['bb_upperband2'] = bollinger2['upper']

        bollinger3 = qtpylib.bollinger_bands(
            qtpylib.typical_price(dataframe), window=20, stds=3
        )
        dataframe['bb_lowerband3'] = bollinger3['lower']
        dataframe['bb_middleband3'] = bollinger3['mid']
        dataframe['bb_upperband3'] = bollinger3['upper']

        bollinger4 = qtpylib.bollinger_bands(
            qtpylib.typical_price(dataframe), window=20, stds=4
        )
        dataframe['bb_lowerband4'] = bollinger4['lower']

        dataframe['min_short'] = ta.MIN(dataframe, timeperiod=EMA_SHORT_TERM)
        dataframe['max_short'] = ta.MAX(dataframe, timeperiod=EMA_SHORT_TERM)

        dataframe['min_medium'] = ta.MIN(dataframe, timeperiod=EMA_MEDIUM_TERM)
        dataframe['max_medium'] = ta.MAX(dataframe, timeperiod=EMA_MEDIUM_TERM)

        dataframe['min_long'] = ta.MIN(dataframe, timeperiod=EMA_LONG_TERM)
        dataframe['max_long'] = ta.MAX(dataframe, timeperiod=EMA_LONG_TERM)

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
            EMA_SHORT_TERM = 5
            EMA_MEDIUM_TERM = 12
            EMA_LONG_TERM = 21
            # GUARDS AND TRENDS
            if 'volume-enabled' in params and params['volume-enabled']:
                conditions.append(dataframe['volume'] < (dataframe['volume'].rolling(window=params['volume-value']).mean().shift(1) * 20))
           
            # TRIGGERS
            if 'trigger' in params:
                if params['trigger'] == 'bb_lower2':
                    conditions.append(dataframe['close'] <= dataframe['bb_lowerband2'])
                if params['trigger'] == 'bb_lower3':
                    conditions.append(dataframe['close'] <= dataframe['bb_lowerband3'])
                if params['trigger'] == 'bb_lower4':
                    conditions.append(dataframe['close'] <= dataframe['bb_lowerband4'])
                if params['trigger'] == 'emaShort':
                    conditions.append(dataframe['close'] < dataframe['ema_{}'.format(EMA_SHORT_TERM)])
                if params['trigger'] == 'emaMedium':
                    conditions.append(dataframe['close'] < dataframe['ema_{}'.format(EMA_MEDIUM_TERM)])
                if params['trigger'] == 'emaLong':
                    conditions.append(dataframe['close'] < dataframe['ema_{}'.format(EMA_LONG_TERM)])
                

            if conditions:
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
            Integer(5, 40, name='volume-value'),
            Categorical([True, False], name='volume-enabled'),
            Categorical(['bb_lower2', 'bb_lower3', 'bb_lower4', 'emaShort', 'emaMedium', 'emaLong'], name='trigger')
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
            conditions = []

            EMA_SHORT_TERM = 5
            EMA_MEDIUM_TERM = 12
            EMA_LONG_TERM = 21

            # GUARDS AND TRENDS
            # TRIGGERS
            if 'trigger' in params:
                if params['trigger'] == 'bb_lower2':
                    conditions.append(dataframe['close'] >= dataframe['bb_lowerband2'])
                if params['trigger'] == 'bb_middle2':
                    conditions.append(dataframe['close'] >= dataframe['bb_middleband2'])
                if params['trigger'] == 'bb_upper2':
                    conditions.append(dataframe['close'] >= dataframe['bb_upperband2'])
                if params['trigger'] == 'bb_upper3':
                    conditions.append(dataframe['close'] >= dataframe['bb_upperband3'])
                if params['trigger'] == 'emaShort':
                    conditions.append(dataframe['close'] < dataframe['ema_{}'.format(EMA_SHORT_TERM)])
                if params['trigger'] == 'emaMedium':
                    conditions.append(dataframe['close'] < dataframe['ema_{}'.format(EMA_MEDIUM_TERM)])
                if params['trigger'] == 'emaLong':
                    conditions.append(dataframe['close'] < dataframe['ema_{}'.format(EMA_LONG_TERM)])
                

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
            Categorical([True, False], name='sell-shortEMA-enabled'),
            Categorical([True, False], name='sell-mediumEMA-enabled'),
            Categorical(['bb_lower2', 'bb_middle2', 'bb_upper2', 'bb_upper3','emaShort', 'emaMedium', 'emaLong'], name='trigger')
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
            Real(-0.3, -0.001, name='stoploss'),
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

        dataframe.loc[
            (dataframe['volume'] < (dataframe['volume'].rolling(window=30).mean().shift(1) * 20)) &
            (dataframe['close'] < dataframe['ema_{}'.format(self.EMA_SHORT_TERM)]) &
            (dataframe['close'] < dataframe['ema_{}'.format(self.EMA_MEDIUM_TERM)]) &
            (dataframe['close'] == dataframe['min']) &
            (dataframe['close'] <= dataframe['bb_lowerband']),
            'buy'
        ] = 1

        return dataframe


    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        dataframe.loc[
            (dataframe['close'] > dataframe['ema_{}'.format(self.EMA_SHORT_TERM)]) &
            (dataframe['close'] > dataframe['ema_{}'.format(self.EMA_MEDIUM_TERM)]) &
            (dataframe['close'] >= dataframe['max']) &
            (dataframe['close'] >= dataframe['bb_middleband']),
            'sell'
        ] = 1

        return dataframe
