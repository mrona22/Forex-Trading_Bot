import pandas as pd
import numpy as np
import logging
import sklearn as sk

# add logging
logging.basicConfig(level=logging.INFO)


def feature_engineering(dataframe):
    """
    Takes in dataframe, with close, high, low, (volume maybe) and returns a dataframe with features:
    - Rolling Mean
    - Stochastic Oscillator %K
    - Williams %R
    - Weighted Close
    - Commodity Channel Index (CCI)
    - 15 Day Moving Average 
    - 15 Day Rolling Standard Deviation
    - Bollinger Bands
    """

    logging.info('Feature Engineering')

    dataframe['rolling_mean'] = dataframe['close'].expanding().mean()

    dataframe['%K'] = ((dataframe['close'] - dataframe['low'].rolling(window=10).min()) / (dataframe['high'].rolling(window=10).max() - dataframe['low'].rolling(window=10).min())) * 100

    dataframe['%R'] = ((dataframe['high'].rolling(window=10).max() - dataframe['close']) / (dataframe['high'].rolling(window=10).max() - dataframe['low'].rolling(window=10).min())) * (-100)

    dataframe['weighted_close'] = (dataframe['high'] + dataframe['low'] + 2 * dataframe['close']) / 4 

    dataframe['CCI'] = (dataframe['weighted_close'] - dataframe['weighted_close'].rolling(window=10).mean()) / (0.015 * dataframe['weighted_close'].rolling(window=10).std())

    dataframe['15_moving_mean'] = dataframe['close'].rolling(window=15).mean()

    dataframe['15_rolling_std'] = dataframe['close'].rolling(window=15).std()

    dataframe['upper_band'] = dataframe['15_moving_mean'] + (2 * dataframe['15_rolling_std'])

    dataframe['lower_band'] = dataframe['15_moving_mean'] - (2 * dataframe['15_rolling_std'])

    return dataframe

def run_diagnostics(dataframe):
    """
    Takes in singular dataframe Analyze Time Series Data:
    TODO: Pattern recognition for Trends 
    TODO: Optimize 
    """
    pass