# Import libraries
import time
import requests
import json


class Downloader:
    def start(self, jobinstructions):
        print("hello world")
        self.download_json()
        print("done")
    #
    def download_json(self):
        items = requests.get('https://api.tvmaze.com/singlesearch/shows?q=narcos&embed=episodes')  # (your url)
        data = items.json()
        with open('data.json', 'w') as f:
            json.dump(data, f)