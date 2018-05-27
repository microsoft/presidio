package stow_test

import (
	"net/url"

	"github.com/graymeta/stow"
)

func init() {
	validatefn := func(config stow.Config) error {
		return nil
	}
	makefn := func(config stow.Config) (stow.Location, error) {
		return &testLocation{
			config: config,
		}, nil
	}
	kindfn := func(u *url.URL) bool {
		return u.Scheme == testKind
	}
	stow.Register(testKind, makefn, kindfn, validatefn)
}

const testKind = "test"

type testLocation struct {
	config stow.Config
}

func (l *testLocation) Close() error {
	return nil
}

func (l *testLocation) CreateContainer(name string) (stow.Container, error) {
	return nil, nil
}
func (l *testLocation) RemoveContainer(id string) error {
	return nil
}

func (l *testLocation) Container(id string) (stow.Container, error) {
	return nil, nil
}
func (l *testLocation) Containers(prefix string, cursor string, count int) ([]stow.Container, string, error) {
	return nil, "", nil
}

func (l *testLocation) ItemByURL(u *url.URL) (stow.Item, error) {
	return nil, nil
}

func (l *testLocation) ContainerByURL(u *url.URL) (stow.Container, error) {
	return nil, nil
}
