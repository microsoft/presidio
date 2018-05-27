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

// ID returns a string value representing the Item, in this case it's the
// name of the object.
func (i *item) ID() string {
	return i.id
}

// Name returns a string value representing the Item, in this case it's the
// name of the object.
func (i *item) Name() string {
	return i.id
}

// URL returns a URL that for the given CloudStorage object.
func (i *item) URL() *url.URL {
	url, _ := url.Parse(i.client.StorageUrl)
	url.Scheme = Kind
	url.Path = path.Join(url.Path, i.container.id, i.id)
	return url
}

// Size returns the size in bytes of the CloudStorage object.
func (i *item) Size() (int64, error) {
	return i.size, nil
}

// Open is a method that returns an io.ReadCloser which represents the content
// of the CloudStorage object.
func (i *item) Open() (io.ReadCloser, error) {
	r, _, err := i.client.ObjectOpen(i.container.id, i.id, false, nil)
	var res io.ReadCloser = r
	// FIXME: this is a workaround to issue https://github.com/graymeta/stow/issues/120
	if s, ok := res.(readSeekCloser); ok {
		res = &fixReadSeekCloser{readSeekCloser: s, item: i}
	}
	return res, err
}

type readSeekCloser interface {
	io.ReadSeeker
	io.Closer
}

type fixReadSeekCloser struct {
	readSeekCloser
	item *item
	read bool
}

func (f *fixReadSeekCloser) Read(p []byte) (int, error) {
	f.read = true
	return f.readSeekCloser.Read(p)
}

func (f *fixReadSeekCloser) Seek(offset int64, whence int) (int64, error) {
	if offset == 0 && whence == io.SeekEnd && !f.read {
		return f.item.size, nil
	}
	return f.readSeekCloser.Seek(offset, whence)
}

// ETag returns a string value representing the CloudStorage Object
func (i *item) ETag() (string, error) {
	return i.hash, nil
}

// LastMod returns a time.Time object representing information on the date
// of the last time the CloudStorage object was modified.
func (i *item) LastMod() (time.Time, error) {
	// If an object is PUT, certain information is missing. Detect
	// if the lastModified field is missing, send a request to retrieve
	// it, and save both this and other missing information so that a
	// request doesn't have to be sent again.
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
