import re
from collections import Counter
from stop_words import get_stop_words
import requests
from bs4 import BeautifulSoup
import nltk
import json
import time
import redis
import uuid
from Jobs.web_scraper import Scraper
from urllib.parse import urlparse

redis_db = redis.StrictRedis(host="localhost", port=6379, db=0)


def insert_success_redis(key, message):
    redis_db.set("joblogs:success:"+key, message)

def insert_failure_redis(key, message):
    redis_db.set("joblogs:failure:"+key, message)


def do_work(params):
    start = time.time()
    try:
        job = params.get('job')
        url = params.get('url')
        key = str(params['job'] + str(uuid.uuid4()))
        funcs = {
            'url': count_and_save_words,
            'hello': say_hello,
            'scrape': Scraper.scrape,
        }
        funcs[job](url)

        # else:
        #     raise Exception("No job found with that name")
        end = time.time()
        total_time = (end - start)
        message = "Job took " + str(total_time) + " seconds"
        # save to redis success
        insert_success_redis(key, message)
        return [{"key": key, "message": message}]

    except Exception as ex:
        end = time.time()
        total_time = (end - start)
        # save to redis failure
        errmsg = str("Error {0}".format(str(ex.args[0])).encode("utf-8"))
        key = str(params['job'] + str(uuid.uuid4()))
        insert_failure_redis(key, errmsg)
        return [{"key":key, "message": errmsg}]


def write_file(result, filename):
    with open(filename, 'w') as file:
        jsonstuff = json.dumps(result)
        print(jsonstuff)
        file.write((jsonstuff))


def count_and_save_words(url):
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
        result = {"url": url, "total": len(raw_word_count), "result_all" : raw_word_count.most_common(10), "result_no_stop_words": no_stop_words_count.most_common(10)}
        write_file(result,filename)
        return result
    except:
        errors.append("Unable to add item to database.")
        return {"error": errors}


def say_hello(url):
    return "Hello" + url
