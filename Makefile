DOCKER_REGISTRY    ?= microsoft
DOCKER_BUILD_FLAGS :=
LDFLAGS            :=

BINS        = presidio-anonymizer presidio-api presidio-scanner presidio-scheduler presidio-datasink presidio-streams
IMAGES      = presidio-anonymizer presidio-api presidio-analyzer presidio-scanner presidio-scheduler presidio-datasink presidio-streams


GIT_TAG   = $(shell git describe --tags --always 2>/dev/null)
VERSION   ?= ${GIT_TAG}
PRESIDIO_LABEL := $(if $(PRESIDIO_LABEL),$(PRESIDIO_LABEL),$(VERSION))
LDFLAGS   += -X github.com/Microsoft/presidio/pkg/version.Version=$(VERSION)

CX_OSES = linux windows darwin
CX_ARCHS = amd64

# Build native binaries
.PHONY: build
build: $(BINS)

.PHONY: $(BINS)
$(BINS): vendor
	go build -ldflags '$(LDFLAGS)' -o bin/$@ ./$@/cmd/$@

build-docker-base: 
	docker build -t presidio-golang -f golang.Dockerfile .
	docker build -t presidio-alpine -f alpine.Dockerfile .


# To use docker-build, you need to have Docker installed and configured. You should also set
# DOCKER_REGISTRY to your own personal registry if you are not pushing to the official upstream.
.PHONY: docker-build
docker-build: build-docker-base
#docker-build: build-docker-bins
docker-build: $(addsuffix -image,$(IMAGES))

%-image:
	docker build $(DOCKER_BUILD_FLAGS) --build-arg VERSION=$(VERSION) -t $(DOCKER_REGISTRY)/$*:$(PRESIDIO_LABEL) -f $*/Dockerfile .

# You must be logged into DOCKER_REGISTRY before you can push.
.PHONY: docker-push
docker-push: $(addsuffix -push,$(IMAGES))

%-push:
	docker push $(DOCKER_REGISTRY)/$*:$(PRESIDIO_LABEL)

# All non-functional tests
.PHONY: test
test: python-test
test: go-test

# All non-functional python tests
.PHONY: python-test
python-test: python-test-unit
# Unit tests. Local only.
.PHONY: python-test-unit
python-test-unit: 
	cd presidio-analyzer
	pytest --log-cli-level=0 

# All non-functional go tests
.PHONY: go-test
go-test: go-test-style
go-test: go-test-unit
# Unit tests. Local only.
.PHONY: go-test-unit
go-test-unit: vendor clean
	-docker rm test-redis -f
	-docker rm test-azure-emulator -f
	docker run --rm --name test-redis -d -p 6379:6379 redis
	go test -v ./...
	docker rm test-redis -f
	
.PHONY: test-functional
test-functional: vendor docker-build
	-docker rm test-presidio-api -f
	-docker rm test-presidio-analyzer -f
	-docker rm test-presidio-anonymizer -f
	-docker network create testnetwork
	docker run --rm --name test-presidio-analyzer --network testnetwork -d -p 3000:3000 -e GRPC_PORT=3000 $(DOCKER_REGISTRY)/presidio-analyzer:$(PRESIDIO_LABEL)
	docker run --rm --name test-presidio-anonymizer --network testnetwork -d -p 3001:3001 -e GRPC_PORT=3001 $(DOCKER_REGISTRY)/presidio-anonymizer:$(PRESIDIO_LABEL)
	docker run --rm --name test-azure-emulator -e executable=blob  -d -t -p 10000:10000 -p 10001:10001 -v ${HOME}/emulator:/opt/azurite/folder arafato/azurite
	docker run --rm --name test-s3-emulator -d -p 9090:9090 -p 9191:9191 -t adobe/s3mock
	sleep 30
	docker run --rm --name test-presidio-api --network testnetwork -d -p 8080:8080 -e WEB_PORT=8080 -e ANALYZER_SVC_HOST=test-presidio-analyzer -e ANALYZER_SVC_PORT=3000 -e ANONYMIZER_SVC_HOST=test-presidio-anonymizer -e ANONYMIZER_SVC_PORT=3001 $(DOCKER_REGISTRY)/presidio-api:$(PRESIDIO_LABEL)
	go test --tags functional ./tests -count=1
	docker rm test-presidio-api -f
	docker rm test-presidio-analyzer -f
	docker rm test-presidio-anonymizer -f
	docker rm test-azure-emulator -f
	docker rm test-s3-emulator -f
	docker network rm testnetwork


.PHONY: go-test-style
go-test-style:
	gometalinter --config ./gometalinter.json ./...

.PHONY: go-format
go-format:
	go list -f '{{.Dir}}' ./... | xargs goimports -w -local github.com/Microsoft/presidio

make-docs: vendor
	docker run --rm -v $(shell pwd)/docs:/out -v $(shell pwd)/pkg/types:/protos pseudomuto/protoc-gen-doc --doc_opt=markdown,proto.md
.PHONY: docs
docs: make-docs

make-proto: vendor
	python -m grpc_tools.protoc -I . --python_out=. --grpc_python_out=. ./*.proto
	protoc -I . --go_out=plugins=grpc:. ./*.proto

.PHONY: proto
proto: make-proto

make-clean:
	-docker rm test-redis -f

.PHONY: clean
clean: make-clean

HAS_GOMETALINTER := $(shell command -v gometalinter 2>/dev/null)
HAS_GIT          := $(shell command -v git 2>/dev/null)
HAS_DOCKER		 := $(shell command -v docker 2>/dev/null)

vendor:
ifndef HAS_GIT
	$(error You must install git)
endif
ifndef HAS_DOCKER
	$(error You must install Docker)
endif
ifndef HAS_GOMETALINTER
	go get -u github.com/alecthomas/gometalinter
	gometalinter --install
endif
	
.PHONY: bootstrap
bootstrap: vendor