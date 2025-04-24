# Docker Engine

* Docker Engine is jargon for the server-side components of Docker that run and manage containers

* Basic Components:
    * docker CLI
        * {API}
    * Docker Engine
        * daemon
    * Plugins and other

* More detail:
    * docker CLI
        * Commands CLI
    * daemon
        * Expose API
    * containerd
        * Lifecycle management (start, stop, delete...)
    * shim
        * Enables pluggable lower level
    * Rc - runc 
        * Interface with kernel
    * Runing containers

* Container-related standars:
    * image-spec
    * runtime-spec
    * distribution-spec

* runc: is the reference implementation of the OCI runtime-spec, low-level.
* containerd: manage lifecycle events such as starting, stopping, and deleting containers, high-level.

* The daemon can expose the API on a local socket or over the network. On Linux, the local socket is `/var/run/docker.sock`
* daemonless containers: is the ability to stop, restart, and even update the Docker daemon without impacting running containers.

* Simmarizes the process
    * docker CLI
        * Convert docker run command into API request and send to API (daemon)
    * daemon
        * Receive API request and instruct containerd to start a new container
    * containerd
        * Receive instruction to create new container and pass instruction to runc
    * shim
        * Becomes container's parent process and communicates with containerd
    * runc
        * Builds new container and exits

## Commands

* `docker pull nginx:latest`
* `docker run -d --name web1 nginx:latest`
* `docker run --name web1 -d --publish 8080:8080 test:latest`
* `docker ps`
* `docker ps -a`
* `docker ps --all`
* `docker rm web1 -f`
