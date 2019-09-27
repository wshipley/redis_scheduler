from rq import Queue
from rq.job import Job
from worker import conn
from requests import request
from flask import Flask, render_template, request
from job_executer import do_work
import rq_dashboard
import json
import uuid
from redis import Redis
from rq.registry import StartedJobRegistry

app = Flask(__name__)

app.config.from_object(rq_dashboard.default_settings)
app.register_blueprint(rq_dashboard.blueprint, url_prefix="/rq")

# app.config.from_object(os.environ['APP_SETTINGS'])
q = Queue(connection=conn)


@app.route("/runningjobs", methods=['GET'])
def running_jobs():
    redis_conn = Redis()
    registry = StartedJobRegistry('default', connection=redis_conn)
    running_job_ids = registry.get_job_ids()  # Jobs which are exactly running.
    expired_job_ids = registry.get_expired_job_ids()
    info = {"running_jobs": running_job_ids, "expired_jobs" : expired_job_ids}
    return json.dumps(info)


@app.route("/results/<job_key>", methods=['GET'])
def get_results(job_key):

    job = Job.fetch(job_key, connection=conn)
    if job.is_finished:
        result = job.result
        results = result
        return json.dumps(results)
    else:
        return "Not ready yet!", 202


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/start', methods=['POST'])
def get_counts():
    # get url
    data = json.loads(request.data.decode())
    job = data["job"]
    url = data.get("url")

    # start job
    jobid = str(uuid.uuid4())
    params = {"url": url, "job": job, 'job_id': jobid}
    job = q.enqueue_call(
        func=do_work, args=(params,), result_ttl=5000, timeout=1000000, job_id=jobid
    )
    # return created job id
    return job.get_id()


if __name__ == "__main__":
    app.run(host='0.0.0.0')
