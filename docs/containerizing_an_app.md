# Containerizing an app

## Basic steps to containerizing an app

* Create your app
* Create the Dockerfile
* Build the image
* Pull to the registry 
* Run as container

## Push the image

Using docker hub or another images hub

## Run the app

Execute

```bash
docker run -it --detach --name targo --publish 8000:8000 janobourian/bank-app:maxine.bankapp
```

## About layers

* Instructions that add content create a Layer
    * FROM
    * RUN
    * COPY
    * WORKDIR
* Instructions that does not add content create metadata
    * EXPOSE
    * ENV
    * CMD
    * ENTRYPOINT

Type `docker history bank-app:maxine.bankapp` to show the instructions
Type `docker inspect bank-app:maxine.bankapp` to see the layers

## Moving to production

* Big is bad!
* Stages is a good way to reduce the Image size

```Dockerfile
FROM folang:1.23.4-alpine AS base
WORKDIR /src
COPY go.mod go.sum .
RUN go mod download
COPY . . 

FROM base AS build-cliente
RUN go build -o /bin/client ./cmd/client

FROM base AS build-server
RUN go build -o /bin/server ./cmd/server

FROM scratch AS prod
COPY --from=build-client /bin/client /bin/
COPY --from=build-server /bin/server /bin/
ENTRYPOINT [ "/bin/server" ]
```

## Buildx, BuildKit, drivers, and Build Cloud

* Client: Buildx
* Server: BuildKit

## Commands

* `docker init`
* `docker build -t bank-app:maxine.bankapp .`
* `docker inspect bank-app:maxine.bankapp`
* `docker login`
* `docker tag <current-tag> <new-tag>`
* `docker tag bank-app:maxine.bankapp janobourian/bank-app:maxine.bankapp`
* `docker push janobourian/bank-app:maxine.bankapp`
* `docker run -it --detach --name targo --publish 8000:8000 janobourian/bank-app:maxine.bankapp`
* `docker history janobourian/bank-app:maxine`
* `docker inspect janobourian/bank-app:maxine`
* `docker buildx ls`
* `docker buildx inspect <BUILDX_NAME>`
* `docker buildx create --driver=docker-container --name=container`
* `docker buildx use container`
* `docker buildx build --builder=container --platform=linux/amd64,linux/arm64 -t janobourian/bank-app:maxine.bankapp --push .`