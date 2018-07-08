
# Development 

## Setting up the environment

It is recommended to work with macOS, Linux or [WSL](https://docs.microsoft.com/en-us/windows/wsl/install-win10)

***Note that the port mapping will conflict with running `make test`***

1. Docker

     ***[How to enable Docker in WSL](https://nickjanetakis.com/blog/setting-up-docker-for-windows-and-wsl-to-work-flawlessly)***

2. Consul
```
docker run --name dev-consul -d -p 8300:8300 -p 8301:8301 -p 8302:8302 -p 8400:8400 -p 8500:8500 -p 8600:8600 consul
```

Consul create volumes to persist data. If the container is stopped, don't remove it. Just start it.

```
docker start dev-consul
```

3. Redis
```
docker run --name dev-redis -d -p 6379:6379 redis
```

4. Install go 1.10 and Python 3.6

5. Install the golang packages via [glide](https://github.com/Masterminds/glide#install)
```
glide up -v
```
***Note you might need to delete the glide cache folder `~/.glide/cache`***

6. Install the Python packages for the analyzer in the `presidium-analyzer` folder
```
pip3 install -r requirements.txt
```

6. Install [librdkafka](https://github.com/confluentinc/confluent-kafka-go#installing-librdkafka)

7. Protobuf generator tools

    * `https://github.com/golang/protobuf`

    * `https://grpc.io/docs/tutorials/basic/python.html`

8. To generate proto files, clone [presidium-genproto](https://github.com/presidium-io/presidium-genproto) and run the following commands in `$GOPATH/src/github.com/presidium-io/presidium-genproto/src` folder

```
python -m grpc_tools.protoc -I . --python_out=. --grpc_python_out=. ./*.proto
```

```
protoc -I . --go_out=plugins=grpc:. ./*.proto
```


## Development notes
- Build the bins with `make build`
- Build the the Docker image with `make docker-build`
- Push the Docker images with `make docker-push`
- Run the tests with `make test`
- Adding a file in go requires the `make go-format` command before running and building the service.

## Load test

1. Create a project.
2. Edit  `post.lua`. Change the template name
3. Run [wrk](https://github.com/wg/wrk)

```
wrk -t2 -c2 -d30s -s post.lua http://<api-service-address>/api/v1/projects/<my-project>/analyze
```
