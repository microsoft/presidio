package azure

import (
	"errors"
	"net/url"
	"strings"
	"time"

	az "github.com/Azure/azure-sdk-for-go/storage"
	"github.com/graymeta/stow"
)

type location struct {
	config stow.Config
	client *az.BlobStorageClient
}

func (l *location) Close() error {
	return nil // nothing to close
}

func (l *location) CreateContainer(name string) (stow.Container, error) {
	err := l.client.GetContainerReference(name).Create(&az.CreateContainerOptions{Access: az.ContainerAccessTypeBlob})
	if err != nil {
		if strings.Contains(err.Error(), "ErrorCode=ContainerAlreadyExists") {
			return l.Container(name)
		}
		return nil, err
	}
	container := &container{
		id: name,
		properties: az.ContainerProperties{
			LastModified: time.Now().Format(timeFormat),
		},
		client: l.client,
	}
	time.Sleep(time.Second * 3)
	return container, nil
}

func (l *location) Containers(prefix, cursor string, count int) ([]stow.Container, string, error) {
	params := az.ListContainersParameters{
		MaxResults: uint(count),
		Prefix:     prefix,
	}
	if cursor != stow.CursorStart {
		params.Marker = cursor
	}
	response, err := l.client.ListContainers(params)
	if err != nil {
		return nil, "", err
	}
	containers := make([]stow.Container, len(response.Containers))
	for i, azureContainer := range response.Containers {
		containers[i] = &container{
			id:         azureContainer.Name,
			properties: azureContainer.Properties,
			client:     l.client,
		}
	}
	return containers, response.NextMarker, nil
}

func (l *location) Container(id string) (stow.Container, error) {
	cursor := stow.CursorStart
	for {
		containers, crsr, err := l.Containers(id[:3], cursor, 100)
		if err != nil {
			return nil, stow.ErrNotFound
		}
		for _, i := range containers {
			if i.ID() == id {
				return i, nil
			}
		}

		cursor = crsr
		if cursor == "" {
			break
		}
	}

	return nil, stow.ErrNotFound
}

func (l *location) ItemByURL(url *url.URL) (stow.Item, error) {
	if url.Scheme != "azure" {
		return nil, errors.New("not valid azure URL")
	}
	location := strings.Split(url.Host, ".")[0]
	a, ok := l.config.Config(ConfigAccount)
	if !ok {
		// shouldn't really happen
		return nil, errors.New("missing " + ConfigAccount + " config")
	}
	if a != location {
		return nil, errors.New("wrong azure URL")
	}
	path := strings.TrimLeft(url.Path, "/")
	params := strings.SplitN(path, "/", 2)
	if len(params) != 2 {
		return nil, errors.New("wrong path")
	}
	c, err := l.Container(params[0])
	if err != nil {
		return nil, err
	}
	return c.Item(params[1])
}

func (l *location) RemoveContainer(id string) error {
	return l.client.GetContainerReference(id).Delete(nil)
}
