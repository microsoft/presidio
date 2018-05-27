package s3

import (
	"fmt"
	"io"
	"net/url"
	"strings"
	"sync"
	"time"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/service/s3"
	"github.com/graymeta/stow"
	"github.com/pkg/errors"
)

// The item struct contains an id (also the name of the file/S3 Object/Item),
// a container which it belongs to (s3 Bucket), a client, and a URL. The last
// field, properties, contains information about the item, including the ETag,
// file name/id, size, owner, last modified date, and storage class.
// see Object type at http://docs.aws.amazon.com/sdk-for-go/api/service/s3/
// for more info.
// All fields are unexported because methods exist to facilitate retrieval.
type item struct {
	// Container information is required by a few methods.
	container *container
	// A client is needed to make requests.
	client *s3.S3
	// properties represent the characteristics of the file. Name, Etag, etc.
	properties properties
	infoOnce   sync.Once
	infoErr    error
	tags       map[string]interface{}
	tagsOnce   sync.Once
	tagsErr    error
}

type properties struct {
	ETag         *string    `type:"string"`
	Key          *string    `min:"1" type:"string"`
	LastModified *time.Time `type:"timestamp" timestampFormat:"iso8601"`
	Owner        *s3.Owner  `type:"structure"`
	Size         *int64     `type:"integer"`
	StorageClass *string    `type:"string" enum:"ObjectStorageClass"`
	Metadata     map[string]interface{}
}

// ID returns a string value that represents the name of a file.
func (i *item) ID() string {
	return *i.properties.Key
}

// Name returns a string value that represents the name of the file.
func (i *item) Name() string {
	return *i.properties.Key
}

// Size returns the size of an item in bytes.
func (i *item) Size() (int64, error) {
	return *i.properties.Size, nil
}

// URL returns a formatted string which follows the predefined format
// that every S3 asset is given.
func (i *item) URL() *url.URL {
	if i.container.customEndpoint == "" {
		genericURL := fmt.Sprintf("https://s3-%s.amazonaws.com/%s/%s", i.container.Region(), i.container.Name(), i.Name())

		return &url.URL{
			Scheme: "s3",
			Path:   genericURL,
		}
	}

	genericURL := fmt.Sprintf("%s/%s", i.container.Name(), i.Name())
	return &url.URL{
		Scheme: "s3",
		Path:   genericURL,
	}
}

// Open retrieves specic information about an item based on the container name
// and path of the file within the container. This response includes the body of
// resource which is returned along with an error.
func (i *item) Open() (io.ReadCloser, error) {
	params := &s3.GetObjectInput{
		Bucket: aws.String(i.container.Name()),
		Key:    aws.String(i.ID()),
	}

	response, err := i.client.GetObject(params)
	if err != nil {
		return nil, errors.Wrap(err, "Open, getting the object")
	}
	return response.Body, nil
}

// LastMod returns the last modified date of the item. The response of an item that is PUT
// does not contain this field. Solution? Detect when the LastModified field (a *time.Time)
// is nil, then do a manual request for it via the Item() method of the container which
// does return the specified field. This more detailed information is kept so that we
// won't have to do it again.
func (i *item) LastMod() (time.Time, error) {
	err := i.ensureInfo()
	if err != nil {
		return time.Time{}, errors.Wrap(err, "retrieving Last Modified information of Item")
	}
	return *i.properties.LastModified, nil
}

// ETag returns the ETag value from the properies field of an item.
func (i *item) ETag() (string, error) {
	return *(i.properties.ETag), nil
}

func (i *item) Metadata() (map[string]interface{}, error) {
	err := i.ensureInfo()
	if err != nil {
		return nil, errors.Wrap(err, "retrieving metadata")
	}
	return i.properties.Metadata, nil
}

func (i *item) ensureInfo() error {
	if i.properties.Metadata == nil || i.properties.LastModified == nil {
		i.infoOnce.Do(func() {
			// Retrieve Item information
			itemInfo, infoErr := i.getInfo()
			if infoErr != nil {
				i.infoErr = infoErr
				return
			}

			// Set metadata field
			i.properties.Metadata, infoErr = itemInfo.Metadata()
			if infoErr != nil {
				i.infoErr = infoErr
				return
			}

			// Set LastModified field
			lmValue, infoErr := itemInfo.LastMod()
			if infoErr != nil {
				i.infoErr = infoErr
				return
			}
			i.properties.LastModified = &lmValue
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

// Tags returns a map of tags on an Item
func (i *item) Tags() (map[string]interface{}, error) {
	i.tagsOnce.Do(func() {
		params := &s3.GetObjectTaggingInput{
			Bucket: aws.String(i.container.name),
			Key:    aws.String(i.ID()),
		}

		res, err := i.client.GetObjectTagging(params)
		if err != nil {
			if strings.Contains(err.Error(), "NoSuchKey") {
				i.tagsErr = stow.ErrNotFound
				return
			}
			i.tagsErr = errors.Wrap(err, "getObjectTagging")
			return
		}

		i.tags = make(map[string]interface{})
		for _, t := range res.TagSet {
			i.tags[*t.Key] = *t.Value
		}
	})

	return i.tags, i.tagsErr
}
