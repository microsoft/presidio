.PHONY: test
WORKSPACE = $(shell pwd)

topdir = /tmp/$(pkg)-$(version)

all: container runcontainer
	@true

container:
	docker build --no-cache -t builder-stow test/

runcontainer:
	docker run -v $(WORKSPACE):/mnt/src/github.com/graymeta/stow builder-stow

deps:
	go get github.com/tebeka/go2xunit
	go get -u github.com/golang/dep/cmd/dep
	dep ensure

test: clean deps vet
	go test -v $(go list ./... | grep -v /vendor/) | tee tests.out
	go2xunit -fail -input tests.out -output tests.xml

vet:
	go vet $(go list ./... | grep -v /vendor/)

clean:
	rm -f tests.out test.xml
