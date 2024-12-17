import os
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

    def on_message(self, ws, message):
        """
        Called function for when a message is received.
        """
        self.data.put(json.loads(message))
        logging.info(f"Received message: {message}")

    def on_error(self, ws, error):
        """
        Called function for when an error occurs.
        """
        logging.error(f"Error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        """
        Called function for when the connection is closed.
        """
        logging.info(f"Connection closed: {close_status_code} - {close_msg}")

    def on_open(self, ws):
        """
        Called function for when the connection is opened and sends a subscribe request
        with specific symbol.
        """
        logging.info("Connection opened.")
        subscribe_message = json.dumps({
            "action": "subscribe",
            "params": {
                "symbols": self.symbol  # Ensure this is a comma-separated string
            }
        })
        ws.send(subscribe_message)

    def connect(self):
        """
        Connects to the websocket.
        """
        websocket_url = f'wss://ws.twelvedata.com/v1/quotes/price?apikey={self.api_key}'
        self.ws = websocket.WebSocketApp(websocket_url,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        self.ws.on_open = self.on_open
        self.ws.run_forever()
    
    def get_data(self):
        """
        Returns the data that has been received. 
        Potenitally waiting for 60 seconds if no data recieved.
        """
        try:
            output = self.data.get(timeout=60)
        except queue.Empty:
            logging.error("No data received, after 60 seconds.")
            output = None
        return output

    

    

    