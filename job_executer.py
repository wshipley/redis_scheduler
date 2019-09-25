import time
import redis
import uuid
from Jobs.web_scraper import Scraper
from Jobs.web_analytics import Analytics
from Jobs.misc_jobs import Miscjobs

redis_db = redis.StrictRedis(host="localhost", port=6379, db=0)

ps = redis_db.pubsub()
ps.subscribe(['default'])
#
# rc.publish('foo', 'hello world')
#
def insert_success_redis(key, message):
    redis_db.publish('default', "joblogs:success:"+key)
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
            'url': Analytics().count_and_save_words,
            'hello': Miscjobs().say_hello,
            'scrape': Scraper().scrape,
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
