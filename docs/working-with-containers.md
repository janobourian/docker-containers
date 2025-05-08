# Working with containers

* To install nano inside gcc:latest docker container `apt-get update && apt-get install nano -y`

## VMs vs Containers

![alt text](images/working-with-containers/image.png)

## Images and containers

* You can start multiple containers from a single image. Images are read-only, but every container has a read-write layer. 

![alt text](images/working-with-containers/image_01.png)

## Pulling image and start container

```bash
docker pull nginx:latest
docker run -it -d --name dashboard --publish 80:80 nginx:latest
docker exec -it dashboard sh
cd /usr/share/nginx/html
```

## How containers start apps

There are three ways you can tell Docker how to start an app in a container:

* An `Entrypoint` instruction in the image
* A `cmd` instruction in the image
* A `cli` argument

## Connecting to a running container

* Interactive
* Remote execution

## Self-healing container with restart policies

* no (default)
* on-failure
* always
* unless-stopped

## Docker commands

* `docker build -t demoapp:latest .`
* `docker run -d --name macorina --publish 8000:8000 demoapp:latest`
* `docker exec -it macorina sh`
* `docker pull python:latest`
* `docker run -it -d --name macarena python:latest`
* `docker exec -u root -it macarena sh`
* `docker run -it --detach --name bang --publish 8000:8000 --env-file .env fastapi:latest`
* `docker inspect nginx:latest | grep Entrypoint -A 3`
* `docker run --rm --detach alpine sleep 60`
* `docker exec -it macarena sh`
* `docker exec macarena ps`
* `docker inspect macarena`
* `docker inspect <CONTAINER_NAME>`
* `docker inspect <IMAGE_NAME>`
* `docker stop macarena`
* `docker restart macarena`
* `docker rm macarena -f`
* `docker run --name neversaydie -it --restart always alpine sh`
* `docker rm ${docker ps -aq) -f`
* `docker rmi $(docker images -q)`