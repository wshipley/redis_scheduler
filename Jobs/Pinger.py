# Import libraries
import time
import requests
import json


class Pinger:
    def start(self, jobinstructions):
        print("hello world")
        self.ping()
        print("done")

    #
    def ping(self):
        items = requests.post('http://localhost:7000/contentListener')  # (your url)
        return items