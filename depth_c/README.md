```bash
docker build -t depthc .
docker run -it --mount type=bind,src=.,dst=/depthc --name depthc-container depthc
```