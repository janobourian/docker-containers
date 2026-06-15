# Docker docs :D

There are paramount concepts about the containers, in this file we will face them.

## Storage

### Volumes

```bash
docker run --mount type=volume,src=frontend,dst=/data --detach --publish 8080:80 frontend
```

### Bind mounts

```bash
docker run --mount type=bind,src=/Users/frgonzal/docker/frontend,dst=/data --detach --publish 8080:80 frontend
docker run --mount type=bind,src=/Users/frgonzal/Documents/maxine/ai_process,dst=/home/maxine -it --detach ai_process
```

## Docker Compose

## Commands


```bash
docker run -i -t ubuntu /bin/bash
docker run --detach --publish 8080:80 docker/welcome-to-docker
docker build -t frontend .
docker run --detach --publish 8080:80 frontend
```