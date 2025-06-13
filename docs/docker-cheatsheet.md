# Docker CheatSheet

## Help

* `docker --help`
* `docker <COMMAND> --help`

## Commands 

* `docker version` - All information about docker
* `docker info` - All information about docker status
* `docker --version` - Only the docker container version
* `docker images` - List all current images in your docker
* `docker pull <IMAGE_NAME>:<VERSION>` - Pull a specific image from docker hub
* `docker run --name <CONTAINER_NAME> --detach --publish <INTERNAL_PORT>:<EXPOSE_PORT> <IMAGE_NAME>:<VERSION>` - Run a container
* `docker ps` - List only active containers
* `docker ps --all` - List all containers
* `docker exec -it <CONTAINER_NAME> <COMMAND>` - Execute some commands in interactive mode
* `docker stop <CONTAINER_NAME>` - Stop a container
* `docker rm <CONTAINER_NAME>` - Delete a container
* `docker rmi <IMAGE_NAME>:<VERSION>` - Delete an image
* `docker build -t <IMAGE_NAME>:<VERSION> .` - Build an image with a specific tag

## Flags 

* `--name string` - The Docker container name
* `[-d | --detach]` - Working on detached mode, working with the container in background
* `[-p | --publish] <INTERNAL_PORT>:<EXPOSE_PORT>`- Port mapping
* `ps [-a | --all]`- List all containers, even those in the stopped state
* `exec [-it | -i -t | --interactive --tty]` - Execute in interactive mode
* `build [-t | --tag]` - Tag an image  