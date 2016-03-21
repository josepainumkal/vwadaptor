vwadaptor
===============================

modelrun service for vw

### Run Locally using docker

docker-compose -f docker-compose.dev.yml build
docker-compose -f docker-compose.dev.yml up

The vwadaptor service should be available at:

```
your-docker-machine-ip:5000
```

The flower monitor should be available at:

```
your-docker-machine-ip:5555
```
