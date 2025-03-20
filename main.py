import threading
import logging
import pandas as pd
import numpy as np
import time
from queue import Queue
from data_fetcher import make_request_series, create_info_series, json_to_pandas
from strategy import run_diagnostics
from websocket_client import WebSocketClient
from dotenv import load_dotenv

def start_socket(client, data_queue):
    """
    Function to start the websocket client and fetch new data.
    """
    client.connect()
    while True:
        available_data = client.data.get()
        if available_data:
            data_queue.put(available_data['price'])

def make_predictions(data_queue, initial_data, predictions):
    """
    Function to make predictions based on new data.
    """
    while True:
        if not data_queue.empty():
            new_data = data_queue.get()
            initial_data = initial_data.append(new_data, ignore_index=True)

            # returns None if the model isn't performing well
            model = run_diagnostics(initial_data)

            if model is not None:
                prediction = model.predict(new_data)
                logging.info(f'Prediction made {prediction}')
                predictions.append(prediction)

            initial_data.append(new_data)
        time.sleep(5)

def main(ticker_symbol):
    """
    Main function to run code for the bot.
    """

    predictions = []
    data_queue = Queue()

    client = WebSocketClient(ticker_symbol)

    initial_data = json_to_pandas(make_request_series(create_info_series(ticker_symbol, '5m')))

    websocket_thread = threading.Thread(target=start_socket, args=(client, data_queue), daemon=True)
    prediction_thread = threading.Thread(target=make_predictions, args=(data_queue, initial_data, predictions), daemon=True)

    websocket_thread.start()
    prediction_thread.start()

    websocket_thread.join()
    prediction_thread.join()