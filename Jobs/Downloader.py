# Import libraries
import time
import requests
import json


class Downloader:
    def start(self, jobinstructions):
        print("hello world")
        url = jobinstructions.get('url')
        self.download_json(url)
        print("done")

    #
    def download_json(self, url):
        items = requests.get(url)  # (your url)
        data = items.json()
        with open('data.json', 'w') as f:
            json.dump(data, f)
