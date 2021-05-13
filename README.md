# Content
* [Run script](#run-script)
* [Build docker container](#build-docker-container)
* [Existing docker container](#existing-docker-container)
* [Reference](#reference)

## Run script

python3 iServer.py localhost 8086 xxxx   
where xxxx is the iServer's address you want to access

## Build Docker container
- Install Docker  
Follow the first two sections of the excellent guide [Getting Started with Docker](https://docs.docker.com/get-started/) if you are not familiar with Docker.  

- Running InfluxDB in Docker  
Pull [official influxdb image](https://hub.docker.com/_/influxdb) and list images locally installed on your computer. (Note please use version 1.8) 
```
docker pull influxdb:1.8
docker image ls
```
You should see influxdb listed.  

Now create a container from this image and run it:
```
docker run -d -p 8086:8086 -v influxdb:/var/lib/influxdb --name influxdb influxdb:1.8
```

You can stop and restart the container by doing:
```
docker container stop influxdb
docker container start influxdb
```

- Grafana  
Use official grafana image by doing:
```
docker pull grafana/grafana
docker run -p 3000:3000 -v grafana:/var/lib/grafana grafana/grafana
```
Port 3000 on the local host is redirected to port 3000 in the grafana container.   
Log in to grafana by pointing your web browser to <http://localhost:3000>. Use the default user and password: admin / admin .  
- Build iserver container  
clone this repo and build container:
```
git clone https://github.com/bdongmd/iServer-docker.git
cd iServer-docker
docker build . -t iserver
```

- Network setting  
The sensor scrip will be running in a container based on the sensor image. So in this container, localhost points to the container itself. Since this container does not run the InfluxDB server, so the script won't find <http://localhost:8086> .  

Docker containers can see each other only if they share the same network. So the solution is to connect the containers to the same network.  
So let's create a network:
```
docker network create mynet
```

Add the influxdb container to this network:
```
docker network connect mynet influxdb
```

- Run container
At last,  run iserver container on the same network:
```
docker run --network mynet iserver
```
If you would like to run the container over a different iServer than the default one used here, run:
```
docker run --network mynet iserver python -u influxdb 8086 ip_addr
```
where `ip_addr` is the ip adress of the iServer you would like to access.


## Existing docker container  
bdongmd/iserver


## Reference
For more details, check [data pipeline with Docker, InfluxDB, and Grafana](https://thedatafrog.com/en/articles/docker-influxdb-grafana/) to see how to setup influxdb with docker.  
