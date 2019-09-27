import redis
import uuid
from rq import Queue
from worker import conn
import json
from job_executer import do_work
redis_db = redis.Redis()

ps = redis_db.pubsub()
ps.subscribe(['default'])
q = Queue(connection=conn)

for item in ps.listen():
    if item['type'] == 'message':
        data = json.loads(item['data'].decode("utf-8"))
        print(data)
        if type(data) is dict and data.get('queuework'):
            job = data["job"]
            # start job
            jobid = str(uuid.uuid4())
            params = {"job": job, 'job_id': jobid, 'url': data['url']}
            job = q.enqueue_call(
                func=do_work, args=(params,), result_ttl=5000, timeout=1000000, job_id=jobid
            )


