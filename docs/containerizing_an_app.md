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