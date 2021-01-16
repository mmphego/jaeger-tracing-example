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


@app.route("/")
def hello_world():
    return "Hello World!"


@app.route("/alpha")
def alpha():
    for i in range(100):
        # removed the colon here since it caused a syntax error - not sure about its purpose?
        do_heavy_work()
        if i % 100 == 99:
            time.sleep(10)
    return "This is the Alpha Endpoint!"


@app.route("/beta")
def beta():
    r = requests.get("https://www.google.com/search?q=python")
    a_dict = {}
    for key, value in r.headers.items():
        print(key, ":", value)
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
    for key, value in r.headers.items()[:50]:
        print(key, ":", value)
        a_dict.update({key: value})
    redis_db.mset(a_dict)
    return jsonify(a_dict)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
