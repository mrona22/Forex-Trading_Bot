import os
import numpy as np
import logging
import websocket
import json
from dotenv import load_dotenv
import queue

class WebsocketClient:
    def __init__(self, api_key, symbol):
        """
        Initialize the Websocket Client, with specific API key.
        Makes it possible to get real-time data.
        """
        self.api_key = api_key
        self.symbol = symbol
        self.ws = None
        self.data = queue.Queue()

    def on_message(self, message):
        """
        Called function for when a message is received.
        """
        self.data.put(json.loads(message))
        logging.info(f"Received message: {message}")

    def on_error(self, error):
        """
        Called function for when an error occurs.
        """
        logging.error(f"Error: {error}")

    def on_close(self):
        """
        Called function for when the connection is closed.
        """
        logging.info("Connection closed.")

    def on_open(self):
        """
        Called function for when the connection is opened and sends a subscribe request
        with specific symbol.
        """
        logging.info("Connection opened.")
        subscribe = {
            "action": "subscribe",
            "params": {
                "symbols": [self.symbol]
            }
        }
        self.ws.send(json.dumps(subscribe))


    def connect(self):
        """
        Connects to the websocket.
        """
        self.ws = websocket.WebSocketApp(f'wss://ws.twelvedata.com/v1/quotes/price?symbol={self.symbol}&apikey={self.api_key}',
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        self.ws.on_open = self.on_open
        self.ws.run_forever()
    
    def get_data(self):
        """
        Returns the data that has been received.
        """
        try:
            output = self.data.get(timeout=60)
        except queue.Empty:
            logging.error("No data received, after 60 seconds.")
            output = None
        return output

    

    

    