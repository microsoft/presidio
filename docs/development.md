
# Development 

## Setting up the environment

1. Docker

***Note that the port mapping will conflict with running `make test`***

2. Redis

```sh
$ docker run --name dev-redis -d -p 6379:6379 redis
```

3. Install go 1.11 and Python 3.7

4. Install the golang packages via [dep](https://github.com/golang/dep/releases)
```sh
$ dep ensure
```

5. Build and install [re2](https://github.com/google/re2)

```sh
$ re2_version="2018-12-01"
$ wget -O re2.tar.gz https://github.com/google/re2/archive/${re2_version}.tar.gz
$ mkdir re2 
$ tar --extract --file "re2.tar.gz" --directory "re2" --strip-components 1
$ cd re2 && make install
```

6. Install the Python packages for the analyzer in the `presidio-analyzer` folder

```sh
$ pip3 install -r requirements.txt
$ pip3 install -r requirements-dev.txt
```

**Note** 
If you encounter errors with `pyre2` than install `cython` first

```sh
$ pip3 install cython
```

7. Protobuf generator tools

    - `https://github.com/golang/protobuf`

    - `https://grpc.io/docs/tutorials/basic/python.html`

8. To generate proto files, clone [presidio-genproto](https://github.com/Microsoft/presidio-genproto) and run the following commands in `$GOPATH/src/github.com/Microsoft/presidio-genproto/src` folder

    ```
    python -m grpc_tools.protoc -I . --python_out=../python --grpc_python_out=../python ./*.proto
    ```

    ```
    protoc -I . --go_out=plugins=grpc:../golang ./*.proto
    ```


## Development notes
- Build the bins with `make build`
- Build the the Docker image with `make docker-build`
- Push the Docker images with `make docker-push`
- Run the tests with `make test`
- Adding a file in go requires the `make go-format` command before running and building the service.
- Run functional tests with `make test-functional`

## Load test

1. Create a project.
2. Edit  `post.lua`. Change the template name
3. Run [wrk](https://github.com/wg/wrk)

```
wrk -t2 -c2 -d30s -s post.lua http://<api-service-address>/api/v1/projects/<my-project>/analyze
```
