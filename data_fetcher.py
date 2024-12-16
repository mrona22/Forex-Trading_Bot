import json
import numpy as np
import pandas as pd
import requests
import time
import re
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("app.log"),
                        logging.StreamHandler()
                    ])

def make_request_series(api_key, info):
    """
    Takes in API, information and constructes the API request and sends it.

    Makes Request similar to this:
    https://api.twelvedata.com/time_series?symbol=AAPL,EUR/USD,ETH/BTC:Huobi,TRP:TSX&interval=1min&apikey=your_api_ke
    """

    request_link= f'https://api.twelvedata.com/time_series?{info}&apikey={api_key}'

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

def make_request_rates(api_key, info):
    """
    Takes in API, information and constructes the API request and sends it 
    
    Makes Request similar to this:
    https://api.twelvedata.com/exchange_rate?symbol=USD/JPY&apikey=your_api_key
    """

    request_link= f'https://api.twelvedata.com/exchange_rate?{info}&apikey={api_key}'

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
    Takes in a list of symbols, intervals and conditionally output_size.

    Creates thee query of the Api request and returns similar to this:
    symbol=AAPL,EUR/USD,ETH/BTC:Huobi,TRP:TSX&interval=1min
    """

    symbol_string = re.sub(r"[ \[\]]", '', str(symbol))

    output = f'symbol={symbol_string}&interval={interval}'

    logging.info(f'created info string: {output}')

    return output if output_size else output + f'&outputsize={output_size}'

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
    to a list of Dataframes
    """
    dataframes = {}
    for symbol, content in json_content.items():
   
        meta = content['meta']
        values = content['values']
        df = pd.DataFrame(values)
        for key, value in meta.items():
            df[key] = value

        dataframes[symbol] = df

    #final_df = pd.concat(dataframes, ignore_index=True)

    return dataframes



