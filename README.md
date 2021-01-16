# jaeger-tracing-example

## Challenge: Python Application Tracing

Site Reliability Engineers (SRE) don't typically work with the production code. They may develop code and additional tooling to make their jobs better, but in terms of what's shipped to the customer, that usually lies squarely with the developers.

For this reason, it will generally be the developers who add tracing components to the code. That being said, maybe you are curious and want to see more about the development side. 

You will need to have a few things to do this:

- Your own container registry (GitHub Repo, DockerHub, etc.).
- Intermediate level knowledge of Python (e.g., you can write the code for a simple Python app).
- Kubernetes Cluster (ideally your K3s cluster on Vagrant).
- Jaeger setup on cluster.

You can find the necessary starter files at this [GitHub Repo](https://github.com/udacity/CNAND_nd064_C4_Observability_Starter_Files/tree/master/course-files/tracing-extra).

## Steps

The `app` directory, contains a `Dockerfile, requirements.txt` and `app.py`. This is a very standard [Flask](https://flask.palletsprojects.com/en/1.1.x/) application. It has 3 routes, each of which does a task and returns a value. Some are broken and some are slow.

There's also a `deployment` directory, which contains `k8s/` [Kubernetes deployment yaml](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/) and `docker/` a [docker-compose yaml](https://docs.docker.com/compose/) file.

## TODOs

Neither have any of the required **tracing components**. You will need to create *spans* to trace in the Flask app and also set up the [*sidecar injection for Jaeger* in the Kubernetes deployment yaml](https://www.jaegertracing.io/docs/1.21/operator/).

- [x] Examine the code in `app/app.py`.
- [x] Modify the Flask application to generate spans on the alpha and beta routes. You should see some starter code for initiating the trace there.
- [x] Use `docker build` and `docker push` to build your Dockerfile and push it to your registry.
- [x] In the `deployment/k8s` folder, examine `deployment.sample.yaml`.
- [x] Change the `deployment.sample.yaml` image to point to your container. Make sure that it is publicly accessible or that you have your authentication credentials set up.
- [x] Add the components to `deployment.sample.yaml` in order for it to trace on Jaeger.
- [x] In your cluster, create a Jaeger instance to deploy in Kubernetes. You can use the `k8s/jaeger.yaml` file.
- [x] Use `kubectl apply` to deploy the deployment yaml.
- [ ] Use `kubectl port-forward` to expose both Jaeger (TCP Port 16686) and the Flask application (TCP port 8080).
- [x] Navigate to `http://localhost/`, `http://localhost/alpha` and `http://localhost/beta`  in a browser.
- [ ] Navigate to your Jaeger UI in the browser and locate the trace.

Now that you have the deployment good to go, it is up to you to find a way to improve the latency of the application. There are many ways to do this and you are welcome to take any approach that achieves the goal of reducing the latency. I've provided one possible approach below, but your solution may be quite different!

When you change the code, be sure to tag it differently from the first docker build. Something like `:v2` will do the trick. You will also need to update the `deployment.sample.yaml` to reflect the new tags.

### Sample Solution

There are a myriad ways you can accomplish this task. One way I did this was to utilize the [Flask-OpenTracing](https://pypi.org/project/Flask-OpenTracing/) library, which simplifies the code that I need to add. This block of code will collect the traces that I need:

```python
config = Config(
    config={
        "sampler": {"type": "const", "param": 1},
        "logging": True,
        "reporter_batch_size": 1,
    },
    service_name="service",
)
jaeger_tracer = config.initialize_tracer()
tracing = FlaskTracing(jaeger_tracer, True, app)
```

This acts as more of a "catch-all" for your application, so it won't necessarily create child spans—but it gives us results that we can use.

### Using Redis

Looking at the `app.py` file, you may have noticed an endpoint named "redis". [Redis](https://redis.io/) is a popular memory store database. It uses a simple key-value structure to store data in memory.

in the `k8s` directory, you will see a subdirectory called `redis`. You deploy both yaml files into your cluster in order to enable a Redis deployment. Then, if you like, you can create a trace on the `redis` endpoint and diagnose why the database write is taking so long.

# Deployment

- `vagrant up`

# Resources

- [How To Implement Distributed Tracing with Jaeger on Kubernetes](https://www.digitalocean.com/community/tutorials/how-to-implement-distributed-tracing-with-jaeger-on-kubernetes)
- [Best Practices for Deploying Jaeger on Kubernetes in Production](https://thenewstack.io/best-practices-for-deploying-jaeger-on-kubernetes-in-production/)

# Credit

- @TheJaySmith
- @Udacity : Cloud Native Architecture - BETA Nanodegree Program
