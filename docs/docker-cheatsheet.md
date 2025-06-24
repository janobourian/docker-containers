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
* `docker start <CONTAINER_NAME>` - Start a specific container
* `docker stop <CONTAINER_NAME>` - Stop a specific container
* `docker restart <CONTAINER_NAME>` - restart a specific container
* `docker init` - Start a container using the docker steps
* `docker tag <CURRENT_TAG> <NEW_TAG>` - Create a tag

## Flags 

* `--name string` - The Docker container name
* `[-d | --detach]` - Working on detached mode, working with the container in background
* `[-p | --publish] <INTERNAL_PORT>:<EXPOSE_PORT>`- Port mapping
* `ps [-a | --all]`- List all containers, even those in the stopped state
* `exec [-it | -i -t | --interactive --tty]` - Execute in interactive mode
* `exec [--user | -u] <USERNAME>` - Execute in interactive mode using a specific user
* `start [-ia | -i -a]` - Attach and interactive mode
* `build [-t | --tag]` - Tag an image
* `run --env-file <LIST_ENV_FILES>` - Use a list of env files
* `run [--rm]` - Automatically remove the container and its associated anonymous volumes when it exits
* `run [--restart]` - Restart policy to apply when a container exits (default "no")

## Compose

* `docker compose version` - To show the docker composer version
* `docker compose up` - Create and start containers
* `docker compose build <SERVICE>` - Build a specific service
* `docker compose down` - Down the services
* `docker compose down -v --remove-orphans` - Remove volumes and remove containers for services not defined in the Compose file
* `docker compose build --no-cache <SERVICE>` - Do not use cache when building the image
* `docker compose ps` - List containers
* `docker compose logs -f` - Follow log output
* `docker compose logs -f <SERVICE>` - Follow log output with specific service

## Images

* `docker inspect <IMAGE_NAME>:<VERSION>`
* `docker history <IMAGE_NAME>:<VERSION>`
* `docker manifest inspect <IMAGE_NAME>:<VERSION>`