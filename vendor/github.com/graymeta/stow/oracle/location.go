package swift

import (
	"errors"
	"net/url"
	"strings"

	"github.com/graymeta/stow"
	"github.com/ncw/swift"
)

type location struct {
	config stow.Config
	client *swift.Connection
}

// Close fulfills the stow.Location interface since there's nothing to close.
func (l *location) Close() error {
	return nil // nothing to close
}

// CreateContainer creates a new container with the given name while returning a
// container instance with the given information.
func (l *location) CreateContainer(name string) (stow.Container, error) {
	err := l.client.ContainerCreate(name, nil)
	if err != nil {
		return nil, err
	}
	container := &container{
		id:     name,
		client: l.client,
	}
	return container, nil
}

// Containers returns a collection of containers based on the given prefix and cursor.
func (l *location) Containers(prefix, cursor string, count int) ([]stow.Container, string, error) {
	params := &swift.ContainersOpts{
		Limit:  count,
		Prefix: prefix,
		Marker: cursor,
	}
	response, err := l.client.Containers(params)
	if err != nil {
		return nil, "", err
	}
	containers := make([]stow.Container, len(response))
	for i, cont := range response {
		containers[i] = &container{
			id:     cont.Name,
			client: l.client,
			// count: cont.Count,
			// bytes: cont.Bytes,
		}
	}
	marker := ""
	if len(response) == count {
		marker = response[len(response)-1].Name
	}
	return containers, marker, nil
}

// Container utilizes the client to retrieve container information based on its
// name.
func (l *location) Container(id string) (stow.Container, error) {
	_, _, err := l.client.Container(id)
	// TODO: grab info + headers
	if err != nil {
		return nil, stow.ErrNotFound
	}

	c := &container{
		id:     id,
		client: l.client,
	}

	return c, nil
}

// ItemByURL returns information on a CloudStorage object based on its name.
func (l *location) ItemByURL(url *url.URL) (stow.Item, error) {

	if url.Scheme != Kind {
		return nil, errors.New("not valid URL")
	}

	path := strings.TrimLeft(url.Path, "/")
	pieces := strings.SplitN(path, "/", 4)

	c, err := l.Container(pieces[2])
	if err != nil {
		return nil, err
	}

	return c.Item(pieces[3])
}

// RemoveContainer attempts to remove a container. Nonempty containers cannot
// be removed.
func (l *location) RemoveContainer(id string) error {
	return l.client.ContainerDelete(id)
}
