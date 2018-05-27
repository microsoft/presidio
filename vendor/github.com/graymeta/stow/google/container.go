package google

import (
	"io"
	"time"

	"github.com/graymeta/stow"
	"github.com/pkg/errors"
	storage "google.golang.org/api/storage/v1"
)

type Container struct {
	// Name is needed to retrieve items.
	name string

	// Client is responsible for performing the requests.
	client *storage.Service
}

// ID returns a string value which represents the name of the container.
func (c *Container) ID() string {
	return c.name
}

// Name returns a string value which represents the name of the container.
func (c *Container) Name() string {
	return c.name
}

func (c *Container) Bucket() (*storage.Bucket, error) {
	return c.client.Buckets.Get(c.name).Do()
}

// Item returns a stow.Item instance of a container based on the
// name of the container
func (c *Container) Item(id string) (stow.Item, error) {
	res, err := c.client.Objects.Get(c.name, id).Do()
	if err != nil {
		return nil, stow.ErrNotFound
	}

	t, err := time.Parse(time.RFC3339, res.Updated)
	if err != nil {
		return nil, err
	}

	u, err := prepUrl(res.MediaLink)
	if err != nil {
		return nil, err
	}

	mdParsed, err := parseMetadata(res.Metadata)
	if err != nil {
		return nil, err
	}

	i := &Item{
		name:         id,
		container:    c,
		client:       c.client,
		size:         int64(res.Size),
		etag:         res.Etag,
		hash:         res.Md5Hash,
		lastModified: t,
		url:          u,
		metadata:     mdParsed,
		object:       res,
	}

	return i, nil
}

// Items retrieves a list of items that are prepended with
// the prefix argument. The 'cursor' variable facilitates pagination.
func (c *Container) Items(prefix string, cursor string, count int) ([]stow.Item, string, error) {
	// List all objects in a bucket using pagination
	call := c.client.Objects.List(c.name).MaxResults(int64(count))

	if prefix != "" {
		call.Prefix(prefix)
	}

	if cursor != "" {
		call = call.PageToken(cursor)
	}

	res, err := call.Do()
	if err != nil {
		return nil, "", err
	}
	containerItems := make([]stow.Item, len(res.Items))

	for i, o := range res.Items {
		t, err := time.Parse(time.RFC3339, o.Updated)
		if err != nil {
			return nil, "", err
		}

		u, err := prepUrl(o.MediaLink)
		if err != nil {
			return nil, "", err
		}

		mdParsed, err := parseMetadata(o.Metadata)
		if err != nil {
			return nil, "", err
		}

		containerItems[i] = &Item{
			name:         o.Name,
			container:    c,
			client:       c.client,
			size:         int64(o.Size),
			etag:         o.Etag,
			hash:         o.Md5Hash,
			lastModified: t,
			url:          u,
			metadata:     mdParsed,
			object:       o,
		}
	}

	return containerItems, res.NextPageToken, nil
}

func (c *Container) RemoveItem(id string) error {
	return c.client.Objects.Delete(c.name, id).Do()
}

// Put sends a request to upload content to the container. The arguments
// received are the name of the item, a reader representing the
// content, and the size of the file.
func (c *Container) Put(name string, r io.Reader, size int64, metadata map[string]interface{}) (stow.Item, error) {
	mdPrepped, err := prepMetadata(metadata)
	if err != nil {
		return nil, err
	}

	object := &storage.Object{
		Name:     name,
		Metadata: mdPrepped,
	}

	res, err := c.client.Objects.Insert(c.name, object).Media(r).Do()
	if err != nil {
		return nil, err
	}

	t, err := time.Parse(time.RFC3339, res.Updated)
	if err != nil {
		return nil, err
	}

	u, err := prepUrl(res.MediaLink)
	if err != nil {
		return nil, err
	}

	mdParsed, err := parseMetadata(res.Metadata)
	if err != nil {
		return nil, err
	}

	newItem := &Item{
		name:         name,
		container:    c,
		client:       c.client,
		size:         size,
		etag:         res.Etag,
		hash:         res.Md5Hash,
		lastModified: t,
		url:          u,
		metadata:     mdParsed,
		object:       res,
	}
	return newItem, nil
}

func parseMetadata(metadataParsed map[string]string) (map[string]interface{}, error) {
	metadataParsedMap := make(map[string]interface{}, len(metadataParsed))
	for key, value := range metadataParsed {
		metadataParsedMap[key] = value
	}
	return metadataParsedMap, nil
}

func prepMetadata(metadataParsed map[string]interface{}) (map[string]string, error) {
	returnMap := make(map[string]string, len(metadataParsed))
	for key, value := range metadataParsed {
		str, ok := value.(string)
		if !ok {
			return nil, errors.Errorf(`value of key '%s' in metadata must be of type string`, key)
		}
		returnMap[key] = str
	}
	return returnMap, nil
}
