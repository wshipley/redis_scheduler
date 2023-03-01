# Import libraries
import time
import requests
import json


class Pinger:
    def start(self, jobinstructions):
        print("hello world")
        print(jobinstructions)
        url = jobinstructions.get('url')
        self.ping(url)
        print("done")

    #
    def ping(self, url):
        items = requests.post(url=url)
        return items