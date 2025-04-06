# Docker Containers Crash Course

## Notes before to start

* The story started with VeamWare and its Virtual Machine
* Some drawbacks:
    * Every OS consumes CPU, RAM, and other resources we'd rather use on applications
    * Every VM and OS needs patching
    * Every VM and OS needs monitoring
    * VM are slow and not very portable
* You can run Linux container on Windows using WSL (Windows Subsystem for Linux)
* Wasm is a WebAssembly:
    * You write your app in your favorite language and compile it as a Wasm binary that will run anywhere you have a Wasm runtime
* Working in AI you need to access to specialized hardware such as:
    * Graphics Processing Units (GPU)
    * Tensor Processing Units (TPU)
    * Neural Processing Units (NPU)
* Docker: Dock Worker
* Major parts to the Docker platform:
    * The CLI (client)
    * The engine (server)
* Container ecosystem:
    * The Open Container Initiative (OCI):
        * main specs:
            * The image-spec
            * The runtime-spec
            * The distribution-spec
    * The CloudNative Computing Foundation (CNCF)
        * phases:
            * Sandbox
            * Incubating
            * Graduated
    * The Moby Project

## Commands

* `docker version` - All information about docker.
* `docker info` - All information about docker status. 
* `docker --version` - Only the version.
* `docker --help` - Fast help.
