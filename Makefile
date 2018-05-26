# The Docker registry where images are pushed.
# Note that if you use an org (like on Quay and DockerHub), you should
# include that: quay.io/foo
DOCKER_REGISTRY    ?= presidium-io
DOCKER_BUILD_FLAGS :=
LDFLAGS            :=

BINS        = presidium-anonymizer presidium-api presidium-scanner presidium-scheduler
IMAGES      = presidium-anonymizer presidium-api presidium-analyzer presidium-scanner presidium-scheduler

GIT_TAG   = $(shell git describe --tags --always 2>/dev/null)
VERSION   ?= ${GIT_TAG}
IMAGE_TAG ?= ${VERSION}
LDFLAGS   += -X github.com/presidium-io/presidium/pkg/version.Version=$(VERSION)

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
	docker build $(DOCKER_BUILD_FLAGS) -t $(DOCKER_REGISTRY)/$*:$(IMAGE_TAG) $*

# You must be logged into DOCKER_REGISTRY before you can push.
.PHONY: docker-push
docker-push: $(addsuffix -push,$(IMAGES))

%-push:
	docker push $(DOCKER_REGISTRY)/$*:$(IMAGE_TAG)

# Cross-compile binaries for our CX targets.
# Mainly, this is for presidium-cross-compile
%-cross-compile: vendor
	@for os in $(CX_OSES); do \
		echo "building $$os"; \
		for arch in $(CX_ARCHS); do \
			GOOS=$$os GOARCH=$$arch CGO_ENABLED=0 go build -ldflags '$(LDFLAGS)' -o ./bin/$*-$$os-$$arch ./$*/cmd/$*; \
		done;\
	done

.PHONY: build-release
build-release: presidium-cross-compile

# All non-functional tests
.PHONY: test
test: test-style
test: test-unit
# Unit tests. Local only.
.PHONY: test-unit
test-unit: vendor
	go test -v ./...

.PHONY: test-functional
test-functional: vendor

.PHONY: test-style
test-style:
	gometalinter --config ./gometalinter.json ./...

.PHONY: format
format: format-go

.PHONY: format-go
format-go:
	go list -f '{{.Dir}}' ./... | xargs goimports -w -local github.com/presidium-io/presidium

HAS_GOMETALINTER := $(shell command -v gometalinter;)
HAS_DEP          := $(shell command -v dep;)
HAS_GIT          := $(shell command -v git;)

vendor:
ifndef HAS_GIT
	$(error You must install git)
endif
ifndef HAS_DEP
	go get -u github.com/golang/dep/cmd/dep
endif
ifndef HAS_GOMETALINTER
	go get -u github.com/alecthomas/gometalinter
	gometalinter --install
endif
	dep ensure


.PHONY: bootstrap
bootstrap: vendor

make-docs:
	docker run --rm -v $(shell pwd)/docs:/out -v $(shell pwd)/pkg/types:/protos pseudomuto/protoc-gen-doc --doc_opt=markdown,proto.md
.PHONY: docs
docs: make-docs

make-proto:
	python -m grpc_tools.protoc -I . --python_out=. --grpc_python_out=. ./*.proto
	protoc -I . --go_out=plugins=grpc:. ./*.proto

.PHONY: proto
proto: make-proto