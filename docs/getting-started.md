# Getting Started

* Get and work with Docker:
   * Docker Desktop
   * Multipass
   * Server installs on Linux

## The Ops perspective

* Images are objects that contain everything an app needs to run
* You can start a new Bash process inside the container

## The Dev perspective

* Containers are all about applications
* Example: 

```Dockerfile
FROM alpine
LABEL maintainer="your-email@example.com"
RUN apk add --update nodejs npm curl
COPY . /src
WORKDIR /src
RUN  npm install
EXPOSE 8080
ENTRYPOINT ["node", "./app.js"]
```

## Commands

* `docker --version`
* `docker version`
* `docker info`
* `docker --help`
* `docker images`
* `docker pull nginx:latest`
* `docker run --name test -d -p 8080:80 nginx:latest`
* `docker ps`
* `docker ps -a`
* `docker exec -it test bash`
* `docker stop test`
* `docker rm test`
* `docker build -t test:latest .`
* `docker run -d --name web1 --publish 8080:8080 test:latest`
* `docker rm web1 -f`
* `docker rmi test:latest`

## Flags

* `--name` - The Docker container name
* `-d/--detach` - Working on detached mode, working with the container in background
* `-p/--publish` - Port mapping 
* `-a/--all` - List all container, even those in the stopped state