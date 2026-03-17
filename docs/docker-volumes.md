# Volumes and persistent data

Volumes are first-class objects in Docker.

## Container with and without volumes

* By default, Docker gives every volume created with the local driver its own directory on the host under `/var/lib/docker/volumes`, sometime you have to use `ls -la /var/lib/docker/volumes/bizvol/_data/` but on Mac `~/Library/Containers/com.docker.docker/Data/Docker.qcow2`
* Docker will use already created container of it creates a new one.
* `docker run -it --name voltainer --mount source=bizvol,target=/vol alpine`
* `docker exec -it voltainer sh`


## Commands

* `docker volume create myvol`
* `docker volume ls`
* `docker volume inspect myvol`
* `docker volume prune`
* `docker volume rm`