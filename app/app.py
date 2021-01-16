import logging
import os
import time

import requests

import redis
import redis_opentracing
from flask import Flask, jsonify
from flask_opentracing import FlaskTracing
from jaeger_client import Config

app = Flask(__name__)

redis_db = redis.Redis(host="redis-primary.default.svc.cluster.local", port=6379, db=0)


def init_tracer(service):
    logging.getLogger("").handlers = []
    logging.basicConfig(format="%(message)s", level=logging.DEBUG)

    config = Config(
        config={"sampler": {"type": "const", "param": 1}, "logging": True},
        service_name=service,
    )

    # this call also sets opentracing.tracer
    return config.initialize_tracer()


# starter code
tracer = init_tracer("test-service")

# not entirely sure but I believe there's a flask_opentracing.init_tracing() missing here
redis_opentracing.init_tracing(tracer, trace_all_classes=False)

with tracer.start_span("first-span") as span:
    span.set_tag("first-tag", "100")


def do_heavy_work():
    pass


@app.route("/")
def hello_world():
    return "Hello World!"


@app.route("/alpha")
def alpha():
    with tracer.start_span("alpha") as span:
        count = 100
        timer = 10
        span.set_tag("iter-tot-count", count)
        for i in range(count):
            with tracer.start_span(f"iter_{i}", child_of=span) as site_span:
                do_heavy_work()
                if i % 100 == 99:
                    time.sleep(timer)
                    site_span.set_tag("request-duration", f"{timer}")

    return "This is the Alpha Endpoint!"


@app.route("/beta")
def beta():
    with tracer.start_span("get-google-search-queries") as span:
        a_dict = {}
        req = requests.get("https://www.google.com/search?q=python")
        span.set_tag("jobs-count", len(req.json()))
        if req.status_code == 200:
            span.set_tag("request-type", "Success")
        else:
            print("Unable to get site")
            span.set_tag("request-type", "Failure")

        for key, value in req.headers.items():
            print(key, ":", value)
            with tracer.start_span(key["Date"], child_of=span) as date_span:
                date_span.set_tag("date-change", "Success")
            a_dict.update({key: value})
    return jsonify(a_dict)


# needed to rename this view to avoid function name collision with redis import
@app.route("/writeredis")
def writeredis():
    # start tracing the redis client
    redis_opentracing.trace_client(redis_db)
    r = requests.get("https://www.google.com/search?q=python")
    a_dict = {}

    # put the first 50 results into a_dict
    for key, value in list(r.headers.items())[:50]:
        print(f"{key}: {value}")
        a_dict.update({key: value})

    try:
        redis_db.mset(a_dict)
    except redis.exceptions.ConnectionError as err:
        print(err)

    return jsonify(a_dict)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
