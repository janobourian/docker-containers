# Working with images

* The most lightweight image is Alpine Linux
* Image registries is where we store images.
    * Build -> Share -> Run
* Image naming and tagging
    * Registry/User-Org/Repository:Image-tag

## Commands

* `docker images`
* `docker pull python:latest`
* `docker run -it --name macarena -d python:latest`
* `docker start -ai macarena`
* `docker pull elixir:latest`
* `docker run -it --name iex_shell -d elixir:latest`
* `docker start -ai iex_shell`
* `docker inspect node:latest`