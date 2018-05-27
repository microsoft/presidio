package swift

import (
	"io"
	"net/url"
	"path"
	"sync"
	"time"

	"github.com/graymeta/stow"
	"github.com/ncw/swift"
)

type item struct {
	id        string
	container *container
	client    *swift.Connection
	//properties az.BlobProperties
	hash         string
	size         int64
	url          url.URL
	lastModified time.Time
	metadata     map[string]interface{}
	infoOnce     sync.Once
	infoErr      error
}

var _ stow.Item = (*item)(nil)

func (i *item) ID() string {
	return i.id
}

func (i *item) Name() string {
	return i.id
}

func (i *item) URL() *url.URL {
	// StorageUrl looks like this:
	// https://lax-proxy-03.storagesvc.sohonet.com/v1/AUTH_b04239c7467548678b4822e9dad96030
	// We want something like this:
	// swift://lax-proxy-03.storagesvc.sohonet.com/v1/AUTH_b04239c7467548678b4822e9dad96030/<container_name>/<path_to_object>
	url, _ := url.Parse(i.client.StorageUrl)
	url.Scheme = Kind
	url.Path = path.Join(url.Path, i.container.id, i.id)
	return url
}

func (i *item) Size() (int64, error) {
	return i.size, nil
}

func (i *item) Open() (io.ReadCloser, error) {
	r, _, err := i.client.ObjectOpen(i.container.id, i.id, false, nil)
	return r, err
}

func (i *item) ETag() (string, error) {
	err := i.ensureInfo()
	if err != nil {
		return "", err
	}
	return i.hash, nil
}

func (i *item) LastMod() (time.Time, error) {
	err := i.ensureInfo()
	if err != nil {
		return time.Time{}, err
	}
	return i.lastModified, nil
}

// Metadata returns a map of key value pairs representing an Item's metadata
func (i *item) Metadata() (map[string]interface{}, error) {
	err := i.ensureInfo()
	if err != nil {
		return nil, err
	}
	return i.metadata, nil
}

// ensureInfo checks the fields that may be empty when an item is PUT.
// Verify if the fields are empty, get information on the item, fill in
// the missing fields.
func (i *item) ensureInfo() error {
	// If lastModified is empty, so is hash. get info on the Item and
	// update the necessary fields at the same time.
	if i.lastModified.IsZero() || i.hash == "" || i.metadata == nil {
		i.infoOnce.Do(func() {
			itemInfo, infoErr := i.getInfo()
			if infoErr != nil {
				i.infoErr = infoErr
				return
			}
			i.hash, i.infoErr = itemInfo.ETag()
			if infoErr != nil {
				i.infoErr = infoErr
				return
			}
			i.lastModified, i.infoErr = itemInfo.LastMod()
			if infoErr != nil {
				i.infoErr = infoErr
				return
			}
			i.metadata, i.infoErr = itemInfo.Metadata()
			if infoErr != nil {
				i.infoErr = infoErr
				return
			}
		})
	}
	return i.infoErr
}

func (i *item) getInfo() (stow.Item, error) {
	itemInfo, err := i.container.getItem(i.ID())
	if err != nil {
		return nil, err
	}
	return itemInfo, nil
}
