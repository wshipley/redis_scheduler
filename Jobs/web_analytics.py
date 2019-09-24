import re
from collections import Counter
from stop_words import get_stop_words
import requests
from bs4 import BeautifulSoup
import nltk
import json
from urllib.parse import urlparse
import uuid
import os

class Analytics:

    def write_file(self, result, filename):
        with open(filename, 'w') as file:
            jsonstuff = json.dumps(result)
            print(jsonstuff)
            file.write((jsonstuff))

    def count_and_save_words(self, url):
        if 'http://' not in url[:7]:
            url = 'http://' + url
        filename = urlparse(url).hostname + "_" + str(uuid.uuid1()) + ".txt"
        errors = []
        try:
            r = requests.get(url)
        except:
            errors.append(
                "Unable to get URL. Please make sure it's valid and try again."
            )
            return {"error": errors}

        # text processing
        raw = BeautifulSoup(r.text).get_text()
        nltk.data.path.append('./nltk_data/')  # set the path
        tokens = nltk.word_tokenize(raw)
        text = nltk.Text(tokens)

        # remove punctuation, count raw words
        nonPunct = re.compile('.*[A-Za-z].*')
        raw_words = [w for w in text if nonPunct.match(w)]
        raw_word_count = Counter(raw_words)

        # stop words
        no_stop_words = [w for w in raw_words if w.lower() not in get_stop_words('en')]
        no_stop_words_count = Counter(no_stop_words)

        # save the results
        try:
            result = {"url": url, "total": len(raw_word_count), "result_all": raw_word_count.most_common(10),
                      "result_no_stop_words": no_stop_words_count.most_common(10)}
            completeName = os.path.join("data", filename)
            self.write_file(result, completeName)
            return result
        except:
            errors.append("Unable to add item to database.")
            return {"error": errors}
