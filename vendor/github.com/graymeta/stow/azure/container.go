package azure

import (
	"io"
	"strings"
	"time"

	az "github.com/Azure/azure-sdk-for-go/storage"
	"github.com/graymeta/stow"
	"github.com/pkg/errors"
)

// The maximum size of an object that can be Put in a single request
const maxPutSize = 256 * 1024 * 1024

// timeFormat is the time format for azure.
var timeFormat = "Mon, 2 Jan 2006 15:04:05 MST"

type container struct {
	id         string
	properties az.ContainerProperties
	client     *az.BlobStorageClient
}

var _ stow.Container = (*container)(nil)

func (c *container) ID() string {
	return c.id
}

func (c *container) Name() string {
	return c.id
}

func (c *container) Item(id string) (stow.Item, error) {
	blob := c.client.GetContainerReference(c.id).GetBlobReference(id)
	err := blob.GetProperties(nil)
	if err != nil {
		if strings.Contains(err.Error(), "404") {
			return nil, stow.ErrNotFound
		}
		return nil, err
	}
	item := &item{
		id:         id,
		container:  c,
		client:     c.client,
		properties: blob.Properties,
	}

	etag := cleanEtag(item.properties.Etag) // Etags returned from this method include quotes. Strip them.
	item.properties.Etag = etag             // Assign the corrected string value to the field.

	return item, nil
}

func (c *container) Items(prefix, cursor string, count int) ([]stow.Item, string, error) {
	params := az.ListBlobsParameters{
		Prefix:     prefix,
		MaxResults: uint(count),
	}
	if cursor != "" {
		params.Marker = cursor
	}
	listblobs, err := c.client.GetContainerReference(c.id).ListBlobs(params)
	if err != nil {
		return nil, "", err
	}
	items := make([]stow.Item, len(listblobs.Blobs))
	for i, blob := range listblobs.Blobs {

		// Clean Etag just in case.
		blob.Properties.Etag = cleanEtag(blob.Properties.Etag)

		items[i] = &item{
			id:         blob.Name,
			container:  c,
			client:     c.client,
			properties: blob.Properties,
		}
	}
	return items, listblobs.NextMarker, nil
}

func (c *container) Put(name string, r io.Reader, size int64, metadata map[string]interface{}) (stow.Item, error) {
	mdParsed, err := prepMetadata(metadata)
	if err != nil {
		return nil, errors.Wrap(err, "unable to create or update Item, preparing metadata")
	}

	name = strings.Replace(name, " ", "+", -1)

	if size > maxPutSize {
		// Do a multipart upload
		err := c.multipartUpload(name, r, size)
		if err != nil {
			return nil, errors.Wrap(err, "multipart upload")
		}
	} else {
		err = c.client.GetContainerReference(c.id).GetBlobReference(name).CreateBlockBlobFromReader(r, nil)
		if err != nil {
			return nil, errors.Wrap(err, "unable to create or update Item")
		}
	}

	err = c.SetItemMetadata(name, mdParsed)
	if err != nil {
		return nil, errors.Wrap(err, "unable to create or update item, setting Item metadata")
	}

	item := &item{
		id:        name,
		container: c,
		client:    c.client,
		properties: az.BlobProperties{
			LastModified:  az.TimeRFC1123(time.Now()),
			Etag:          "",
			ContentLength: size,
		},
	}
	return item, nil
}

func (c *container) SetItemMetadata(itemName string, md map[string]string) error {
	blob := c.client.GetContainerReference(c.id).GetBlobReference(itemName)
	blob.Metadata = md
	return blob.SetMetadata(nil)
}

func parseMetadata(md map[string]string) (map[string]interface{}, error) {
	rtnMap := make(map[string]interface{}, len(md))
	for key, value := range md {
		rtnMap[key] = value
	}
	return rtnMap, nil
}

func prepMetadata(md map[string]interface{}) (map[string]string, error) {
	rtnMap := make(map[string]string, len(md))
	for key, value := range md {
		str, ok := value.(string)
		if !ok {
			return nil, errors.Errorf(`value of key '%s' in metadata must be of type string`, key)
		}
		rtnMap[key] = str
	}
	return rtnMap, nil
}

func (c *container) RemoveItem(id string) error {
	return c.client.GetContainerReference(c.id).GetBlobReference(id).Delete(nil)
}

// Remove quotation marks from beginning and end. This includes quotations that
// are escaped. Also removes leading `W/` from prefix for weak Etags.
//
// Based on the Etag spec, the full etag value (<FULL ETAG VALUE>) can include:
// - W/"<ETAG VALUE>"
// - "<ETAG VALUE>"
// - ""
// Source: https://tools.ietf.org/html/rfc7232#section-2.3
//
// Based on HTTP spec, forward slash is a separator and must be enclosed in
// quotes to be used as a valid value. Hence, the returned value may include:
// - "<FULL ETAG VALUE>"
// - \"<FULL ETAG VALUE>\"
// Source: https://www.w3.org/Protocols/rfc2616/rfc2616-sec2.html#sec2.2
//
// This function contains a loop to check for the presence of the three possible
// filler characters and strips them, resulting in only the Etag value.
func cleanEtag(etag string) string {
	for {
		// Check if the filler characters are present
		if strings.HasPrefix(etag, `\"`) {
			etag = strings.Trim(etag, `\"`)

		} else if strings.HasPrefix(etag, `"`) {
			etag = strings.Trim(etag, `"`)

		} else if strings.HasPrefix(etag, `W/`) {
			etag = strings.Replace(etag, `W/`, "", 1)

		} else {

			break
		}
	}

	return etag
}
