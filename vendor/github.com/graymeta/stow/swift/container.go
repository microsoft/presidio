package swift

import (
	"io"
	"strings"

	"github.com/pkg/errors"

	"github.com/graymeta/stow"
	"github.com/ncw/swift"
)

type container struct {
	id     string
	client *swift.Connection
}

var _ stow.Container = (*container)(nil)

func (c *container) ID() string {
	return c.id
}

func (c *container) Name() string {
	return c.id
}

func (c *container) Item(id string) (stow.Item, error) {
	return c.getItem(id)
}

func (c *container) Items(prefix, cursor string, count int) ([]stow.Item, string, error) {
	params := &swift.ObjectsOpts{
		Limit:  count,
		Marker: cursor,
		Prefix: prefix,
	}
	objects, err := c.client.Objects(c.id, params)
	if err != nil {
		return nil, "", err
	}
	items := make([]stow.Item, len(objects))
	for i, obj := range objects {

		items[i] = &item{
			id:           obj.Name,
			container:    c,
			client:       c.client,
			hash:         obj.Hash,
			size:         obj.Bytes,
			lastModified: obj.LastModified,
		}
	}
	marker := ""
	if len(objects) == count {
		marker = objects[len(objects)-1].Name
	}
	return items, marker, nil
}

func (c *container) Put(name string, r io.Reader, size int64, metadata map[string]interface{}) (stow.Item, error) {
	mdPrepped, err := prepMetadata(metadata)
	if err != nil {
		return nil, errors.Wrap(err, "unable to create or update Item, preparing metadata")
	}

	headers, err := c.client.ObjectPut(c.id, name, r, false, "", "", mdPrepped)
	if err != nil {
		return nil, errors.Wrap(err, "unable to create or update Item")
	}

	mdParsed, err := parseMetadata(headers)
	if err != nil {
		return nil, errors.Wrap(err, "unable to create or update Item, parsing metadata")
	}

	item := &item{
		id:        name,
		container: c,
		client:    c.client,
		size:      size,
		metadata:  mdParsed,
	}
	return item, nil
}

func (c *container) RemoveItem(id string) error {
	return c.client.ObjectDelete(c.id, id)
}

func (c *container) getItem(id string) (*item, error) {
	info, headers, err := c.client.Object(c.id, id)
	if err != nil {
		if strings.Contains(err.Error(), "Object Not Found") {
			return nil, stow.ErrNotFound
		}
		return nil, errors.Wrap(err, "error retrieving item")
	}

	md, err := parseMetadata(headers)
	if err != nil {
		return nil, errors.Wrap(err, "unable to retrieve Item information, parsing metadata")
	}

	item := &item{
		id:           id,
		container:    c,
		client:       c.client,
		hash:         info.Hash,
		size:         info.Bytes,
		lastModified: info.LastModified,
		metadata:     md,
	}
	return item, nil
}

// Keys are returned as all lowercase, dashes are allowed
func parseMetadata(md swift.Headers) (map[string]interface{}, error) {
	m := make(map[string]interface{}, len(md))
	for key, value := range md.ObjectMetadata() {
		m[key] = value
	}
	return m, nil
}

// TODO determine invalid keys.
func prepMetadata(md map[string]interface{}) (map[string]string, error) {
	m := make(map[string]string, len(md))
	for key, value := range md {
		str, ok := value.(string)
		if !ok {
			return nil, errors.New("could not convert key value") // add a msg mentioning strings only?
		}
		m["X-Object-Meta-"+key] = str
	}
	return m, nil
}
