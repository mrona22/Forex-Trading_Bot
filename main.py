import threading
import pandas as pd
import numpy as np
import time
from data_fetcher import make_request_series, create_info_series, json_to_pandas
from strategy import run_diagnostics
from websocket_client import WebSocketClient
from dotenv import load_dotenv

def start_socket(client):
    """
    Function to start the websocket client.
    """
    client.connect()



def main(ticker_symbol):
    """
    Main function to run code for the bot. 

    TODO: Get initial data and implement and optimize machine learning model
    TODO: Initialize and start the websocket client
    TODO: Using the model and the new data make pattern recognition and make decisions
    """

    client = WebSocketClient(ticker_symbol)

    initial_data = json_to_pandas(make_request_series(create_info_series(ticker_symbol, '5m')))

    websocket_thread = threading.Thread(target=start_socket, args=(client,), daemon=True)

    websocket_thread.start()

    while True:
        available_data  = client.data.get()

        if available_data:

            new_data = available_data['price']

            # Create a decision function which makes a decision based on the new data

            # decision = decision_function(new_data)

            # if decision:

            
            



    
    

