import time
import redis
import uuid
import json
from Jobs.web_scraper import Scraper
from Jobs.web_analytics import Analytics
from Jobs.misc_jobs import Miscjobs
from Jobs.Downloader import Downloader
from Jobs.Pinger import Pinger
from rq.decorators import job

redis_db = redis.StrictRedis(host="localhost", port=6379, db=0)

ps = redis_db.pubsub()
ps.subscribe(['default'])


def _insert_success_redis(key, message):
    msg = json.dumps({"jobid": key, "status": "success", "message": message})
    redis_db.publish('default', msg)
    redis_db.set("joblogs:success:"+key, message)


def _insert_failure_redis(key, message):
    msg = json.dumps({"jobid": key, "status": "failure", "message": message})
    redis_db.publish('default', msg)
    redis_db.set("joblogs:failure:"+key, message)


# @job('low', connection=my_redis_conn, timeout=5)
# def add(x, y):
#     return x + y
#
# job = add.delay(3, 4)
# time.sleep(1)
# print(job.result)
def do_work(params):
    jobid = params.get('job_id')
    msg = json.dumps({"job": jobid, "status": "started"})
    redis_db.publish('default', msg)

    start = time.time()
    try:
        job = params.get('job')
        jobinstructions = params
        key = str(jobid)
        funcs = {
            'analytics': Analytics().count_and_save_words,
            'blah': Miscjobs().say_hello,
            'scrape': Scraper().scrape,
            'downloader': Downloader().start,
            'pinger': Pinger().start
        }
        funcs[job](jobinstructions)

        # else:
        #     raise Exception("No job found with that name")
        end = time.time()
        total_time = (end - start)
        message = "Job took " + str(total_time) + " seconds"
        # save to redis success
        _insert_success_redis(key, message)
        return [{"key": key, "message": message}]

    except Exception as ex:
        end = time.time()
        total_time = (end - start)
        # save to redis failure
        errmsg = str("Error {0}".format(str(ex.args[0])).encode("utf-8"))
        key = str(params['job'] + str(uuid.uuid4()))
        _insert_failure_redis(key, errmsg)
        return [{"key":key, "message": errmsg}]
