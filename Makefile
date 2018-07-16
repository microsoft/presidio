DOCKER_REGISTRY    ?= praesidio
DOCKER_BUILD_FLAGS :=
LDFLAGS            :=

BINS        = presidio-anonymizer presidio-api presidio-scanner presidio-scheduler presidio-registrator
IMAGES      = presidio-anonymizer presidio-api presidio-analyzer presidio-scanner presidio-scheduler presidio-registrator

GIT_TAG   = $(shell git describe --tags --always 2>/dev/null)
VERSION   ?= ${GIT_TAG}
presidio_LABEL := $(if $(presidio_LABEL),$(presidio_LABEL),latest)
LDFLAGS   += -X github.com/presid-io/presidio/pkg/version.Version=$(VERSION)

CX_OSES = linux windows darwin
CX_ARCHS = amd64

# Build native binaries
.PHONY: build
build: $(BINS)

.PHONY: $(BINS)
$(BINS): vendor
	go build -ldflags '$(LDFLAGS)' -o bin/$@ ./$@/cmd/$@

# Cross-compile for Docker+Linux
build-docker-bins: $(addsuffix -docker-bin,$(BINS))

%-docker-bin: vendor
	GOOS=linux GOARCH=amd64 CGO_ENABLED=0 go build -ldflags '$(LDFLAGS)' -o ./$*/rootfs/$* ./$*/cmd/$*

# To use docker-build, you need to have Docker installed and configured. You should also set
# DOCKER_REGISTRY to your own personal registry if you are not pushing to the official upstream.
.PHONY: docker-build
docker-build: build-docker-bins
docker-build: $(addsuffix -image,$(IMAGES))

%-image:
	docker build $(DOCKER_BUILD_FLAGS) -t $(DOCKER_REGISTRY)/$*:$(presidio_LABEL) $*

# You must be logged into DOCKER_REGISTRY before you can push.
.PHONY: docker-push
docker-push: $(addsuffix -push,$(IMAGES))

%-push:
	docker push $(DOCKER_REGISTRY)/$*:$(presidio_LABEL)

# Cross-compile binaries for our CX targets.
# Mainly, this is for presidio-cross-compile
%-cross-compile: vendor
	@for os in $(CX_OSES); do \
		echo "building $$os"; \
		for arch in $(CX_ARCHS); do \
			GOOS=$$os GOARCH=$$arch CGO_ENABLED=0 go build -ldflags '$(LDFLAGS)' -o ./bin/$*-$$os-$$arch ./$*/cmd/$*; \
		done;\
	done

.PHONY: build-release
build-release: presidio-cross-compile

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
	docker run --rm --name test-consul -d -p 8300:8300 -p 8301:8301 -p 8302:8302 -p 8400:8400 -p 8500:8500 -p 8600:8600 consul
	docker run --rm --name test-redis -d -p 6379:6379 redis
	docker run --rm --name test-azure-emulator -e executable=blob  -d -t -p 10000:10000 -p 10001:10001 -v ${HOME}/emulator:/opt/azurite/folder arafato/azurite
	go test -v ./...
	docker rm test-redis -f
	docker rm test-consul -f
	docker rm test-azure-emulator -f
.PHONY: test-functional
test-functional: vendor

.PHONY: go-test-style
go-test-style:
	gometalinter --config ./gometalinter.json ./...

.PHONY: go-format
go-format:
	go list -f '{{.Dir}}' ./... | xargs goimports -w -local github.com/presid-io/presidio

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
	-docker rm test-consul -f
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