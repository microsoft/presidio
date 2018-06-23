
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

5. Install vendored packages via [glide](https://github.com/Masterminds/glide#install)
```
glide up -v
```

6. Protobuf generator tools

    * `https://github.com/golang/protobuf`

    * `https://grpc.io/docs/tutorials/basic/python.html`

7. To generate proto files, run the following commands in `$GOPATH/src/github.com/presidium-io/presidium/pkg/types` folder

```
python -m grpc_tools.protoc -I . --python_out=. --grpc_python_out=. ./*.proto
```

```
protoc -I . --go_out=plugins=grpc:. ./*.proto
```
