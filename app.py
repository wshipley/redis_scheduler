from rq import Queue
from rq.job import Job
from requests import request
from flask import Flask, render_template, request
from job_executer import do_work
import rq_dashboard
import json
import uuid
from redis import Redis
from rq.registry import StartedJobRegistry
from rq.registry import FailedJobRegistry
from rq.registry import FinishedJobRegistry
from rq.registry import ScheduledJobRegistry
from rq_scheduler import Scheduler
from flask_socketio import send, emit
from flask_socketio import SocketIO
import pickle

scheduler = Scheduler(connection=Redis())

app = Flask(__name__)

app.config.from_object(rq_dashboard.default_settings)
app.register_blueprint(rq_dashboard.blueprint, url_prefix="/rq")
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

queue = Queue(connection=Redis())


# app.config.from_object(os.environ['APP_SETTINGS'])

@socketio.on('message')
def handle_message(message):
    send(message)


@socketio.on('json')
def handle_json(json):
    send(json, json=True)


@socketio.on('my event')
def handle_my_custom_event(json):
    emit('my response', json)


@app.route("/schedulejob", methods=['POST'])
def schedule_job():
    data = json.loads(request.data.decode())
    url = data.get("url")
    job = data.get("job")
    interval = int(data.get("interval"))
    jobid = str(uuid.uuid4())

    params = {"url": url, "job": job, 'job_id': jobid}
    blah = scheduler.schedule(
        scheduled_time=datetime.utcnow(),  # Time for first execution, in UTC timezone
        func=do_work,  # Function to be queued
        args=(params,),  # Arguments passed into function when executed
        # kwargs={'foo': 'bar'},  # Keyword arguments passed into function when executed
        interval=interval,  # Time before the function is called again, in seconds
        # repeat=10,  # Repeat this number of times (None means repeat forever)
        meta={'foo': 'bar'}  # Arbitrary pickleable data on the job itself
    )
    redis_conn = Redis()
    jobinfo = {"Name": job, "URL": url, "CRON": None, "Interval": interval, 'Scheduler_id': blah.id, "Job_id": jobid}
    job_key = 'jobsdetails:' + blah.id
    p_mydict = pickle.dumps(jobinfo)
    redis_conn.set(job_key, p_mydict)

    read_dict = redis_conn.get(job_key)
    yourdict = pickle.loads(read_dict)

    # scheduler.cron(
    #     "* * * * *",  # A cron string (e.g. "0 0 * * 0")
    #     func=do_work,  # Function to be queued
    #     args=(params,),  # Arguments passed into function when executed
    #     # kwargs={'foo': 'bar'},  # Keyword arguments passed into function when executed
    #     queue_name='default',  # In which queue the job should be put in
    #     meta={'foo': 'bar'},  # Arbitrary pickleable data on the job itself
    #     use_local_timezone=False  # Interpret hours in the local timezone
    # )
    # Schedule a job to run 10 minutes, 1 hour and 1 day later
    # data = json.loads(request.data.decode())
    # job = data["job"]
    # url = data.get("url")

    # scheduler.enqueue_in(timedelta(seconds=5), do_work, params)
    return json.dumps(yourdict)


@app.route("/cancel", methods=['post'])
def cancel():
    data = json.loads(request.data.decode())
    # redis_conn = Redis()
    # redis_conn.delete(data.get('job_id'))
    result = scheduler.cancel(data.get('job_id'))
    return result


@app.route("/runningjobs", methods=['GET'])
def running_jobs():
    redis_conn = Redis()
    registry = StartedJobRegistry('default', connection=redis_conn)
    fregistry = FinishedJobRegistry('default', connection=redis_conn)
    failed_registry = FailedJobRegistry('default', connection=redis_conn)
    running_job_ids = registry.get_job_ids()  # Jobs which are exactly running.
    expired_job_ids = registry.get_expired_job_ids()
    completed = fregistry.get_job_ids()
    failed = failed_registry.get_job_ids()
    scheduled_jobs = scheduler.get_jobs(with_times=True)
    jobs_to_list = []
    for x in scheduled_jobs:
        blah = x[0].return_value()
        redis_conn.hget(name='jobdetails', key=blah['job_id'])
        to_return = x[0].id, x[0].return_value()
        jobs_to_list.append(to_return)
    info = {"running_jobs": running_job_ids, "expired_jobs": expired_job_ids, "scheduled_jobs": jobs_to_list,
            "completed": completed, "failed": failed}

    return json.dumps(info)


@app.route("/futurejobs")
def getfutre_jobs():
    list_of_job_instances = scheduler.get_jobs(until=timedelta(hours=1))
    future_jobs = []
    for x in list_of_job_instances:
        print(x)
        blah = {"description": x.description, "time_to_run": x.enqueued_at}
        future_jobs.append(blah)
    return json.dumps(future_jobs, default=str)


@app.route("/scheduledjobs", methods=['get', 'post'])
def get_scheduled_jobs():
    redis_conn = Redis()
    registry = ScheduledJobRegistry('default', connection=redis_conn)
    scheduled_jobs = scheduler.get_jobs(with_times=True)
    jobs = []
    for x in scheduled_jobs:
        blah = x[0].return_value()
        job_key = 'jobsdetails:' + x[0].id

        read_dict = redis_conn.get(job_key)
        yourdict = pickle.loads(read_dict)
        returnvalue = {"schedulerid": x[0].id, "jobid":x[0].return_value()[0].get("key"), "message":x[0].return_value()[0].get("message")}
        jobs.append(returnvalue)
    return json.dumps(jobs)


@app.route("/results/<job_key>", methods=['GET'])
def get_results(job_key):
    redis_conn = Redis()
    job = Job.fetch(id=job_key, connection=redis_conn)
    if job.is_finished:
        result = job.return_value()
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
    job = queue.enqueue_call(
        func=do_work, args=(params,), result_ttl=5000, timeout=1000000, job_id=jobid
    )
    return job.get_id()


from datetime import datetime, timedelta
from redis import Redis

#
# if __name__ == "__main__":
#     main()
# socketio.run(app).run(host='0.0.0.0', port=5000)
app.run(host='0.0.0.0', port=5000)
