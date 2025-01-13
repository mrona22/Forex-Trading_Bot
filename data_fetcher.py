import os
import numpy as np
import pandas as pd
import requests
import time
import re
import logging
from dotenv import load_dotenv

# Load the API key from the .env file
load_dotenv()

API_KEY = os.getenv('API_KEY')


# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("app.log"),
                        logging.StreamHandler()
                    ])

def make_request_series(info):
    """
    Takes in API, information and constructes the API request and sends it.

    Makes Request similar to this:
    https://api.twelvedata.com/time_series?symbol=AAPL,EUR/USD,ETH/BTC:Huobi,TRP:TSX&interval=1min&apikey=your_api_ke
    """

    request_link= f'https://api.twelvedata.com/time_series?{info}&apikey={API_KEY}'

    try:
        time.sleep(0.5)

        req = requests.get(request_link)

        req.raise_for_status()

        data = req.json()

    except requests.exceptions.HTTPError as http_err:
        logging.error(f'HTTP error occurred: {http_err}')
        return None
    
    except Exception as err:
        logging.error(f'Other error occurred: {err}')
        raise err
    
    return data



def create_info_series(symbol, interval, output_size=None):
    """
    Takes in a list or individual of symbols, intervals and conditionally output_size.

    Creates thee query of the Api request and returns similar to this:
    symbol=AAPL,EUR/USD,ETH/BTC:Huobi,TRP:TSX&interval=1min
    """

    symbol_string = re.sub(r"[ \[\]\"']", '', str(symbol))

    output = f'symbol={symbol_string}&interval={interval}'

    logging.info(f'created info string: {output}')

    if output_size is not None:
        output += f'&outputsize={output_size}'
    
    return output

def create_info_rates(symbol, date=None):
    """
    Takes in a list of symbols and creates the query of the Api request and returns similar to this:
    symbol=USD/JPY
    """

    symbol_string = re.sub(r"[ \[\]]", '', str(symbol))

    output = f'symbol={symbol_string}'

    logging.info(f'created info string: {output}')

    return output if date else output + f'&date={date}'

def json_to_pandas(json_content):
    """
    Takes in a json that was returned from the API call, converts and returns
    to a dataframe.
    """
    df = pd.DataFrame(json_content['values'])
    
    df = transform_dataframe(df) 

    df = (
        df
        .sort_values(by='datetime')
        .set_index('datetime')
    )

    logging.info('Dataframe created')

    return df

def transform_dataframe(df):
    """
    Takes in a dataframe and transforms columns to date time or float
    In the case there is no volume, it will not be transformed.
    """
    try:
        df['datetime'] = pd.to_datetime(df['datetime'])

        df['open'] = df['open'].astype(float)

        df['high'] = df['high'].astype(float)

        df['low'] = df['low'].astype(float)

        df['close'] = df['close'].astype(float)

        df['volume'] = df['volume'].astype(float)

    except KeyError:
        logging.info('No volume in the dataframe')

        df['datetime'] = pd.to_datetime(df['datetime'])

        df['open'] = df['open'].astype(float)

        df['high'] = df['high'].astype(float)

        df['low'] = df['low'].astype(float)

        df['close'] = df['close'].astype(float)
    
    return df

def update_central_data(info):
    """
    Called with an info string, created by the create_info_series function.
    Loads in form the data.csv file, makes a request to the API and updates the dataframe.
    saves the updated dataframe back to the data.csv file.
    """

    logging.info('Updating data.csv called')

    try:
        df = pd.read_csv('data.csv')

    except FileNotFoundError:
        logging.error('File not found')
        df = pd.DataFrame()

    if not df.empty:

        df = transform_dataframe(df)

        df = df.set_index('datetime')

    updated_info = json_to_pandas(make_request_series(info))

    combined_df = pd.concat([df, updated_info])

    combined_df = combined_df[~combined_df.index.duplicated(keep='last')]

    updated_info.to_csv('data.csv')

    logging.info('Updated data.csv')

    return combined_df




