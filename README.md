# About

This is a bare bones demonstration project for Docker and/or Kubernetes.

It is a REST API that exposes everything needed to play within Docker or Kubernetes

**Assumption**: The environment variable `TUTORIAL_HOME` points to the base path of the project (the path containing the project `.git/` directory).

- [About](#about)
- [Building the Application](#building-the-application)
- [Docker Testing](#docker-testing)
  - [Building the Base Image](#building-the-base-image)
  - [Building the Application Image](#building-the-application-image)
  - [Starting the app in Docker](#starting-the-app-in-docker)


# Building the Application

The `.gitignore` file excludes the built application, so depending on your needs, checkout the relevant branch of the application and prepare a build:

```bash
$ rm -frR dist/
$ git checkout <app-version>
$ python3 setup.py sdist
```

# Docker Testing

## Building the Base Image

Run the following to build the base image:

```bash
$ cd $TUTORIAL_HOME/docker/base
$ docker image rm sample-base
$ docker build --no-cache -t sample-base .
$ cd $TUTORIAL_HOME/
```

## Building the Application Image

Run the following commands to build the application image:

```bash
$ cp -vf dist/* $TUTORIAL_HOME/docker/app
$ cd $TUTORIAL_HOME/docker/app
$ docker image rm sample-api
$ docker build --no-cache -t sample-api .
$ cd $TUTORIAL_HOME/
```

## Starting the app in Docker

Run the following commands to start the application:

```bash
$ docker container stop sample-api-service
$ docker container rm sample-api-service
$ docker run --name sample-api-service \
-p 0.0.0.0:8280:8080 \
-m 128M --memory-swap 128M \
--cpu-quota 25000 \
-d sample-api:latest
```

Making sure everything works:

```bash
$ docker container ls
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS                              NAMES
daf8abb38c2e        sample-api:latest   "gunicorn -w 1 -b 0.…"   32 seconds ago      Up 30 seconds       0.0.0.0:8280->8080/tcp             sample-api-service

$ curl -vvv http://localhost:8280/version
*   Trying ::1...
* TCP_NODELAY set
* Connected to localhost (::1) port 8280 (#0)
> GET /version HTTP/1.1
> Host: localhost:8280
> User-Agent: curl/7.64.1
> Accept: */*
>
< HTTP/1.1 200 OK
< Server: gunicorn/20.0.4
< Date: Tue, 28 Jul 2020 04:28:10 GMT
< Connection: close
< Content-Type: application/json
< Content-Length: 21
<
{"version": "1.0.0"}
* Closing connection 0


$ docker logs sample-api-service
[2020-07-28 04:26:57 +0000] [1] [INFO] Starting gunicorn 20.0.4
[2020-07-28 04:26:58 +0000] [1] [INFO] Listening at: http://0.0.0.0:8080 (1)
[2020-07-28 04:26:58 +0000] [1] [INFO] Using worker: sync
[2020-07-28 04:26:58 +0000] [8] [INFO] Booting worker with pid: 8
172.17.0.1 - - [28/Jul/2020:04:28:10 +0000] "GET /version HTTP/1.1" 200 21 "-" "curl/7.64.1"
```
