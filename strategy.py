import pandas as pd
import numpy as np
import logging
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split

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
    - Voltatility
    """

    logging.info('Feature Engineering')

    dataframe = dataframe.reset_index().sort_values('datetime').set_index('datetime')

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

def label_data(dataframe, ratio_SLTP = 3):
    """
    Takes in dataframe returned from the feature Engeneer and the ration of (Take-Profit Order) / (Stop-Loss Order) labels data
    - 1: Buy
    - 0: Hold
    - -1: Sell
    """

    logging.info('Labeling Data')

    dataframe['TP'] = dataframe['close'] + (ratio_SLTP * dataframe['15_rolling_std'])
    dataframe['SL'] = dataframe['close'] - dataframe['15_rolling_std']

    reached_pos = dataframe['close'].rolling(15).max() >= dataframe['TP']
    reached_neg = dataframe['close'].rolling(15).min() <= dataframe['SL']

    # Here we have to decide later, after testing whether reaching the TP and SL is overfitting to the data
    # Hence should I label them anything or just let them be 0
    dataframe['label'] = reached_pos.astype(int) - reached_neg.astype(int)

   
    return dataframe.drop(columns=['TP', 'SL'])

def run_diagnostics(dataframe):
    """
    Takes in singular dataframe Analyze Time Series Data:
    TODO: Pattern recognition for Trends 
    TODO: Optimize 
    """
    
    train_X, test_X, train_y, test_y = train_test_split(dataframe.drop(columns=['label']), dataframe['label'], test_size=0.2, shuffle=False)

    model = SVC()

    model.fit(train_X, train_y)

    if model.score(test_X, test_y) > 0.5:
        logging.info('Model is performing well')
        return SVC().fit(dataframe.drop(columns=['label']), dataframe['label'])
    else:
        logging.info('Model is not performing well')
        return None


