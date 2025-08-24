# Docker and Wasm

* Evolution
    * Virtual Machines -> Containers -> WebAssembly

## Pre-reqs

* Docker Desktop 4.37+
* Rust 1.82+
* Spin 3.1+
* To see the Wasm version on your Docker Desktop
`docker run --rm -i --privileged --pid=host jorgeprendes420/docker-desktop-shim-manager:latest`

## Create Docker Container

```Dockerfile
FROM scratch
COPY /target/wasm32-wasip1/release/hello_world.wasm .
COPY spin.toml .
```

## Commands

* `spin new hello-world -t http-rust`
* `cd hello-world`
* `spin build`
* `spin up`
* `docker build --platform=wasi/wasm --provenance=false -t rustc-app:wasm .`
* `docker run -t --detach --name wasm-ctr --runtime=io.containerd.spin.v2 --platform=wasi/wasm --publish 5556:80 rustc-app:wasm`