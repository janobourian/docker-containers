# Working with images

* The most lightweight image is Alpine Linux
* Image registries is where we store images.
    * Build -> Share -> Run
* Image naming and tagging
    * Registry/User-Org/Repository:Image-tag
* Images are a collection of loosely connected read-only layers where each layer comprises one or more files.
* Content hashes vs distribution hashes
    * Content hash
    * Distribution hash
* Multi-architecture images
    * Manifest lists
        * A list of architectures supported by an image tag
    * Manifests

## buildx

* `buildx` command makes it easy to create multi-architecture images. 
    * Emulation
    * Build Cloud

## Commands

* `docker images`
* `docker pull python:latest`
* `docker run -it --name macarena -d python:latest`
* `docker start -ai macarena`
* `docker pull elixir:latest`
* `docker run -it --name iex_shell -d elixir:latest`
* `docker start -ai iex_shell`
* `docker inspect node:latest`
* `docker history node:latest`
* `docker manifest inspect nginx:latest` 
* `docker pull gcc`
* `docker run -it --name samba gcc:latest bash`
* `docker images --digests alphine:latest`
* `docker buildx imagetools inspect amazonlinux:latest`
* `docker scout quickview nginx:latest`
* `docker images -q`
* `docker rmi $(docker images -q) -f`