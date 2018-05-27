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

func (l *location) Close() error {
	return nil // nothing to close
}

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

func (l *location) ItemByURL(url *url.URL) (stow.Item, error) {

	if url.Scheme != Kind {
		return nil, errors.New("not valid swift URL")
	}

	path := strings.TrimLeft(url.Path, "/")
	pieces := strings.SplitN(path, "/", 4)

	// swift://lax-proxy-03.storagesvc.sohonet.com/v1/AUTH_b04239c7467548678b4822e9dad96030/<container_name>/<path_to_object>

	c, err := l.Container(pieces[2])
	if err != nil {
		return nil, err
	}

	return c.Item(pieces[3])
}

func (l *location) RemoveContainer(id string) error {
	return l.client.ContainerDelete(id)
}
