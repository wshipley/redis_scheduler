from rq import Queue
from rq.job import Job
from worker import conn
from requests import request
from flask import Flask, render_template, request, jsonify
from job_executer import do_work
import rq_dashboard
import json

app = Flask(__name__)

app.config.from_object(rq_dashboard.default_settings)
app.register_blueprint(rq_dashboard.blueprint, url_prefix="/rq")

# app.config.from_object(os.environ['APP_SETTINGS'])
q = Queue(connection=conn)


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
    params = {"url": url, "job": job}

    job = q.enqueue_call(
        func=do_work, args=(params,), result_ttl=5000, timeout=1000000
    )
    # return created job id
    return job.get_id()


if __name__ == "__main__":
    app.run(host='0.0.0.0')
