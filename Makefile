DOCKER_REGISTRY    ?= presidio.azurecr.io
DOCKER_BUILD_FLAGS :=
LDFLAGS            :=

BINS        		= presidio-anonymizer presidio-ocr presidio-anonymizer-image presidio-api presidio-scheduler presidio-datasink presidio-collector presidio-recognizers-store presidio-tester
GOLANG_IMAGES      	= presidio-anonymizer presidio-ocr presidio-anonymizer-image presidio-api presidio-scheduler presidio-datasink presidio-collector presidio-recognizers-store presidio-tester
PYTHON_IMAGES      	= presidio-analyzer
IMAGES      		= $(GOLANG_IMAGES)  $(PYTHON_IMAGES)
GOLANG_DEPS			= presidio-golang-deps
PYTHON_DEPS			= presidio-python-deps
GOLANG_BASE			= presidio-golang-base
# Python vars used to build wheel
PIP_EXTRA_INDEX_URL = # PIP endpoint url (Azure Artifacts)
WHEEL_VERSION 		= # Presidio python wheel versioning
GIT_TAG   			= $(shell git describe --tags --always 2>/dev/null)
VERSION   			?= ${GIT_TAG}
PRESIDIO_LABEL 		:= $(if $(PRESIDIO_LABEL),$(PRESIDIO_LABEL),$(VERSION))
PRESIDIO_DEPS_LABEL := $(if $(PRESIDIO_DEPS_LABEL),$(PRESIDIO_DEPS_LABEL),'latest')
CURRENT_DIR		 	:= $(shell pwd)
LDFLAGS   			+= -X github.com/microsoft/presidio/pkg/version.Version=$(VERSION)
TEST_IN_CONTAINER	:=
CX_OSES 			= linux windows darwin
CX_ARCHS 			= amd64

# Build native binaries
.PHONY: build
build: $(BINS)

.PHONY: $(BINS)
$(BINS): vendor
	go build -ldflags '$(LDFLAGS)' -o bin/$@ ./$@/cmd/$@


.PHONY: docker-build-deps
docker-build-deps:
	-docker pull $(DOCKER_REGISTRY)/$(GOLANG_DEPS):$(PRESIDIO_DEPS_LABEL) || echo "\nCould not pull base Go image from registry, building locally. If you planned to build locally, the previous error message can be ignored\n"
	-docker pull $(DOCKER_REGISTRY)/$(PYTHON_DEPS):$(PRESIDIO_DEPS_LABEL) || echo "\nCould not pull base Python image from registry, building locally (If you planned to build images locally, the previous error message can be ignored\n"
	docker build -t $(DOCKER_REGISTRY)/$(GOLANG_DEPS):$(PRESIDIO_DEPS_LABEL) -f Dockerfile.golang.deps .
	docker build -t $(DOCKER_REGISTRY)/$(PYTHON_DEPS):$(PRESIDIO_DEPS_LABEL) -f Dockerfile.python.deps .

.PHONY: docker-build-base
docker-build-base:
	-docker pull $(DOCKER_REGISTRY)/$(GOLANG_BASE):$(PRESIDIO_BRANCH_LABEL) || echo "\nCould not pull shared base Go image from registry, building locally. If you planned to build locally, the previous error message can be ignored\n"
	docker build --build-arg REGISTRY=$(DOCKER_REGISTRY) --cache-from=$(DOCKER_REGISTRY)/$(GOLANG_BASE):$(PRESIDIO_BRANCH_LABEL) --build-arg PRESIDIO_DEPS_LABEL=$(PRESIDIO_DEPS_LABEL) -t $(DOCKER_REGISTRY)/$(GOLANG_BASE) -f Dockerfile.golang.base .
	docker tag $(DOCKER_REGISTRY)/$(GOLANG_BASE) $(DOCKER_REGISTRY)/$(GOLANG_BASE):$(PRESIDIO_LABEL)


# To use docker-build, you need to have Docker installed and configured. You should also set
# DOCKER_REGISTRY to your own personal registry if you are not pushing to the official upstream.
.PHONY: docker-build
docker-build: docker-build-golang
docker-build: docker-build-python

.PHONY: docker-build-golang
docker-build-golang: docker-build-golang-base
docker-build-golang: $(addsuffix -dimage,$(GOLANG_IMAGES))

.PHONY: docker-build-golang-single
docker-build-golang-single: $(addsuffix -dimage,$(GOLANG_IMAGE))

.PHONY: docker-build-golang-base
docker-build-golang-base: docker-build-base

.PHONY: docker-build-python
docker-build-python: $(addsuffix -dpypiimage,$(PYTHON_IMAGES))


%-dimage:
	docker build $(DOCKER_BUILD_FLAGS) --build-arg REGISTRY=$(DOCKER_REGISTRY) --build-arg VERSION=$(VERSION) --build-arg PRESIDIO_DEPS_LABEL=$(PRESIDIO_DEPS_LABEL) --build-arg PRESIDIO_BASE_LABEL=$(PRESIDIO_LABEL) -t $(DOCKER_REGISTRY)/$*:$(PRESIDIO_LABEL) -f $*/Dockerfile .

%-dpypiimage:
# Switching between build of python container for local/dev and the one used in presidio automated CI.
# in local/dev environment the container is built with Dockerfile.local which uses the local dev environment and code.
# in the automated CI process, PIP_EXTRA_INDEX_URL is defined and Dockerfile is built which uses the published wheel.
ifndef PIP_EXTRA_INDEX_URL
	docker build $(DOCKER_BUILD_FLAGS) --build-arg REGISTRY=$(DOCKER_REGISTRY) --build-arg VERSION=$(VERSION) --build-arg PRESIDIO_DEPS_LABEL=$(PRESIDIO_DEPS_LABEL) -t $(DOCKER_REGISTRY)/$*:$(PRESIDIO_LABEL) -f $*/Dockerfile.local .
else
	docker build $(DOCKER_BUILD_FLAGS) --build-arg REGISTRY=$(DOCKER_REGISTRY) --build-arg PIP_EXTRA_INDEX_URL=$(PIP_EXTRA_INDEX_URL) --build-arg VERSION=$(WHEEL_VERSION) --build-arg PRESIDIO_DEPS_LABEL=$(PRESIDIO_DEPS_LABEL) -t $(DOCKER_REGISTRY)/$*:$(PRESIDIO_LABEL) -f $*/Dockerfile .
endif

# You must be logged into DOCKER_REGISTRY before you can push.
.PHONY: docker-push-latest-deps
docker-push-latest-deps:
	docker pull $(DOCKER_REGISTRY)/$(PYTHON_DEPS):$(PRESIDIO_DEPS_LABEL)
	docker pull $(DOCKER_REGISTRY)/$(GOLANG_DEPS):$(PRESIDIO_DEPS_LABEL)
	docker image tag $(DOCKER_REGISTRY)/$(PYTHON_DEPS):$(PRESIDIO_DEPS_LABEL) $(DOCKER_REGISTRY)/$(PYTHON_DEPS):latest
	docker image tag $(DOCKER_REGISTRY)/$(GOLANG_DEPS):$(PRESIDIO_DEPS_LABEL) $(DOCKER_REGISTRY)/$(GOLANG_DEPS):latest
	docker push $(DOCKER_REGISTRY)/$(PYTHON_DEPS):latest
	docker push $(DOCKER_REGISTRY)/$(GOLANG_DEPS):latest

PHONY: docker-push-latest-branch-deps
docker-push-latest-branch-deps:
	docker pull $(DOCKER_REGISTRY)/$(PYTHON_DEPS):$(PRESIDIO_DEPS_LABEL)
	docker pull $(DOCKER_REGISTRY)/$(GOLANG_DEPS):$(PRESIDIO_DEPS_LABEL)
	docker image tag $(DOCKER_REGISTRY)/$(PYTHON_DEPS):$(PRESIDIO_DEPS_LABEL) $(DOCKER_REGISTRY)/$(PYTHON_DEPS):$(PRESIDIO_BRANCH_LABEL)
	docker image tag $(DOCKER_REGISTRY)/$(GOLANG_DEPS):$(PRESIDIO_DEPS_LABEL) $(DOCKER_REGISTRY)/$(GOLANG_DEPS):$(PRESIDIO_BRANCH_LABEL)
	docker push $(DOCKER_REGISTRY)/$(PYTHON_DEPS):$(PRESIDIO_BRANCH_LABEL)
	docker push $(DOCKER_REGISTRY)/$(GOLANG_DEPS):$(PRESIDIO_BRANCH_LABEL)

# push with the given label
.PHONY: docker-push
docker-push: docker-push-python
docker-push: docker-push-golang

.PHONY: docker-push-python
docker-push-python: $(addsuffix -push,$(PYTHON_IMAGES))

.PHONY: docker-push-golang
docker-push-golang: $(addsuffix -push,$(GOLANG_IMAGES))

.PHONY: docker-push-golang-single
docker-push-golang-single: $(addsuffix -push,$(GOLANG_IMAGE))

%-push:
	docker push $(DOCKER_REGISTRY)/$*:$(PRESIDIO_LABEL)

.PHONY: docker-push-latest-branch
docker-push-latest-branch: $(addsuffix -push-latest-branch,$(IMAGES))

%-push-latest-branch:
	docker pull $(DOCKER_REGISTRY)/$*:$(PRESIDIO_LABEL)
	docker image tag $(DOCKER_REGISTRY)/$*:$(PRESIDIO_LABEL) $(DOCKER_REGISTRY)/$*:$(PRESIDIO_BRANCH_LABEL)
	docker push $(DOCKER_REGISTRY)/$*:$(PRESIDIO_BRANCH_LABEL)

# pull an existing image tag, tag it again with a provided release tag and 'latest' tag
.PHONY: docker-push-release
docker-push-release: $(addsuffix -push-release,$(IMAGES))

%-push-release:
ifeq ($(RELEASE_VERSION),)
	$(warning RELEASE_VERSION is not set)
else
	docker pull $(DOCKER_REGISTRY)/$*:$(PRESIDIO_LABEL)
	docker image tag $(DOCKER_REGISTRY)/$*:$(PRESIDIO_LABEL) $(DOCKER_REGISTRY)/$*:$(RELEASE_VERSION)
	docker image tag $(DOCKER_REGISTRY)/$*:$(PRESIDIO_LABEL) $(DOCKER_REGISTRY)/public/$*:$(RELEASE_VERSION)
	docker image tag $(DOCKER_REGISTRY)/$*:$(PRESIDIO_LABEL) $(DOCKER_REGISTRY)/public/$*:latest
	docker image tag $(DOCKER_REGISTRY)/$*:$(PRESIDIO_LABEL) $(DOCKER_REGISTRY)/$*:latest
	docker push $(DOCKER_REGISTRY)/$*:$(RELEASE_VERSION)
	docker push $(DOCKER_REGISTRY)/public/$*:$(RELEASE_VERSION)
	docker push $(DOCKER_REGISTRY)/$*:latest
	docker push $(DOCKER_REGISTRY)/public/$*:latest
endif

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
	cd presidio-analyzer && pipenv run pytest --log-cli-level=0 -v

# All non-functional go tests
.PHONY: go-test
# go-test: go-test-style # opting this out until fixing bug https://github.com/microsoft/presidio/issues/262
go-test: go-test-unit
# Unit tests. Local only.
.PHONY: go-test-unit
go-test-unit: vendor
	go test -v `go list ./... | grep -v /presctl`

.PHONY: test-functional
test-functional: docker-build
test-functional:test-functional-no-build

.PHONY: test-functional-no-build
test-functional-no-build:
	-docker rm test-azure-emulator -f
	-docker rm test-kafka -f
	-docker rm test-redis -f
	-docker rm test-s3-emulator -f
	-docker rm test-presidio-api -f
	-docker rm test-presidio-analyzer -f
	-docker rm test-presidio-anonymizer -f
	-docker rm test-presidio-anonymizer-image -f
	-docker rm test-presidio-ocr -f
	-docker rm test-presidio-recognizers-store -f

	-docker network create testnetwork
	docker run --rm --name test-azure-emulator --network testnetwork -e executable=blob  -d -t -p 10000:10000 -p 10001:10001 -v ${HOME}/emulator:/opt/azurite/folder arafato/azurite &
	docker run --rm --name test-kafka -d -p 2181:2181 -p 9092:9092 --env ADVERTISED_HOST=127.0.0.1 --env ADVERTISED_PORT=9092 spotify/kafka &
	docker run --rm --name test-redis --network testnetwork -d -p 6379:6379 redis &
	docker run --rm --name test-s3-emulator --network testnetwork -d -p 9090:9090 -p 9191:9191 -t adobe/s3mock &
	docker run --rm --name test-presidio-anonymizer --network testnetwork -d -p 3001:3001 -e GRPC_PORT=3001 $(DOCKER_REGISTRY)/presidio-anonymizer:$(PRESIDIO_LABEL) &
	docker run --rm --name test-presidio-anonymizer-image --network testnetwork -d -p 3002:3002 -e GRPC_PORT=3002 $(DOCKER_REGISTRY)/presidio-anonymizer-image:$(PRESIDIO_LABEL) &
	docker run --rm --name test-presidio-ocr --network testnetwork -d -p 3003:3003 -e GRPC_PORT=3003 $(DOCKER_REGISTRY)/presidio-ocr:$(PRESIDIO_LABEL) &
	docker run --rm --name test-presidio-recognizers-store --network testnetwork -d -p 3004:3004 -e GRPC_PORT=3004 -e REDIS_URL=test-redis:6379 $(DOCKER_REGISTRY)/presidio-recognizers-store:$(PRESIDIO_LABEL) &
	docker run --rm --name test-presidio-analyzer --network testnetwork -d -p 3000:3000 -e GRPC_PORT=3000 -e RECOGNIZERS_STORE_SVC_ADDRESS=test-presidio-recognizers-store:3004 $(DOCKER_REGISTRY)/presidio-analyzer:$(PRESIDIO_LABEL)
	# wait for containers to start
	sleep 30
	docker run --rm --name test-presidio-api --network testnetwork -d -p 8080:8080 -e WEB_PORT=8080 -e ANALYZER_SVC_ADDRESS=test-presidio-analyzer:3000 -e ANONYMIZER_SVC_ADDRESS=test-presidio-anonymizer:3001 -e ANONYMIZER_IMAGE_SVC_ADDRESS=test-presidio-anonymizer-image:3002 -e OCR_SVC_ADDRESS=test-presidio-ocr:3003 -e RECOGNIZERS_STORE_SVC_ADDRESS=test-presidio-recognizers-store:3004 $(DOCKER_REGISTRY)/presidio-api:$(PRESIDIO_LABEL)
	# wait for api to start
	sleep 10

ifeq ($(TEST_IN_CONTAINER),)
	go test --tags functional ./functional-tests -count=1
else
	-mkdir test-results
	docker run --rm -v "$(CURRENT_DIR)/test-results":/test-result-pipe  --name presidio-tests  --network host $(DOCKER_REGISTRY)/functional-tests:$(PRESIDIO_LABEL)
endif
	-docker rm test-presidio-api -f
	-docker rm test-presidio-analyzer -f
	-docker rm test-presidio-anonymizer -f
	-docker rm test-presidio-anonymizer-image -f
	-docker rm test-presidio-ocr -f
	-docker rm test-azure-emulator -f
	-docker rm test-kafka -f
	-docker rm test-redis -f
	-docker rm test-s3-emulator -f
	-docker rm test-presidio-recognizers-store -f
	-docker network rm testnetwork


.PHONY: go-test-style
go-test-style:
	gometalinter --config ./gometalinter.json `go list ./... | grep -v /presctl`

.PHONY: go-format
go-format:
	go list -f '{{.Dir}}' ./... | xargs goimports -w -local github.com/microsoft/presidio

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
	curl -L https://git.io/vp6lP | sh
endif

.PHONY: bootstrap
bootstrap: vendor