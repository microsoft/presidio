package stow

import (
	"errors"
	"io"
	"net/url"
	"sync"
	"time"
)

var (
	lock sync.RWMutex // protects locations, kinds and kindmatches
	// kinds holds a list of location kinds.
	kinds = []string{}
	// locations is a map of installed location providers,
	// supplying a function that creates a new instance of
	// that Location.
	locations = map[string]func(Config) (Location, error){}
	// configurations is a map of installed location providers,
	// supplying a function that validates the configuration
	configurations = map[string]func(Config) error{}
	// kindmatches is a slice of functions that take turns
	// trying to match the kind of Location for a given
	// URL. Functions return an empty string if it does not
	// match.
	kindmatches []func(*url.URL) string
)

var (
	// ErrNotFound is returned when something could not be found.
	ErrNotFound = errors.New("not found")
	// ErrBadCursor is returned by paging methods when the specified
	// cursor is invalid.
	ErrBadCursor = errors.New("bad cursor")
)

var (
	// CursorStart is a string representing a cursor pointing
	// to the first page of items or containers.
	CursorStart = ""

	// NoPrefix is a string representing no prefix. It can be used
	// in any function that asks for a prefix value, but where one is
	// not appropriate.
	NoPrefix = ""
)

// IsCursorEnd checks whether the cursor indicates there are no
// more items or not.
func IsCursorEnd(cursor string) bool {
	return cursor == ""
}

// Location represents a storage location.
type Location interface {
	io.Closer
	// CreateContainer creates a new Container with the
	// specified name.
	CreateContainer(name string) (Container, error)
	// Containers gets a page of containers
	// with the specified prefix from this Location.
	// The specified cursor is a pointer to the start of
	// the containers to get. It it obtained from a previous
	// call to this method, or should be CursorStart for the
	// first page.
	// count is the number of items to return per page.
	// The returned cursor can be checked with IsCursorEnd to
	// decide if there are any more items or not.
	Containers(prefix string, cursor string, count int) ([]Container, string, error)
	// Container gets the Container with the specified
	// identifier.
	Container(id string) (Container, error)
	// RemoveContainer removes the container with the specified ID.
	RemoveContainer(id string) error
	// ItemByURL gets an Item at this location with the
	// specified URL.
	ItemByURL(url *url.URL) (Item, error)
}

// Container represents a container.
type Container interface {
	// ID gets a unique string describing this Container.
	ID() string
	// Name gets a human-readable name describing this Container.
	Name() string
	// Item gets an item by its ID.
	Item(id string) (Item, error)
	// Items gets a page of items with the specified
	// prefix for this Container.
	// The specified cursor is a pointer to the start of
	// the items to get. It it obtained from a previous
	// call to this method, or should be CursorStart for the
	// first page.
	// count is the number of items to return per page.
	// The returned cursor can be checked with IsCursorEnd to
	// decide if there are any more items or not.
	Items(prefix, cursor string, count int) ([]Item, string, error)
	// RemoveItem removes the Item with the specified ID.
	RemoveItem(id string) error
	// Put creates a new Item with the specified name, and contents
	// read from the reader.
	Put(name string, r io.Reader, size int64, metadata map[string]interface{}) (Item, error)
}

// Item represents an item inside a Container.
// Such as a file.
type Item interface {
	// ID gets a unique string describing this Item.
	ID() string
	// Name gets a human-readable name describing this Item.
	Name() string
	// URL gets a URL for this item.
	// For example:
	// local: file:///path/to/something
	// azure: azure://host:port/api/something
	//    s3: s3://host:post/etc
	URL() *url.URL
	// Size gets the size of the Item's contents in bytes.
	Size() (int64, error)
	// Open opens the Item for reading.
	// Calling code must close the io.ReadCloser.
	Open() (io.ReadCloser, error)
	// ETag is a string that is different when the Item is
	// different, and the same when the item is the same.
	// Usually this is the last modified datetime.
	ETag() (string, error)
	// LastMod returns the last modified date of the file.
	LastMod() (time.Time, error)
	// Metadata gets a map of key/values that belong
	// to this Item.
	Metadata() (map[string]interface{}, error)
}

// Taggable represents a taggable Item
type Taggable interface {
	// Tags returns a list of tags that belong to a given Item
	Tags() (map[string]interface{}, error)
}

// Config represents key/value configuration.
type Config interface {
	// Config gets a string configuration value and a
	// bool indicating whether the value was present or not.
	Config(name string) (string, bool)
	// Set sets the configuration name to specified value
	Set(name, value string)
}

// Register adds a Location implementation, with two helper functions.
// makefn should make a Location with the given Config.
// kindmatchfn should inspect a URL and return whether it represents a Location
// of this kind or not. Code can call KindByURL to get a kind string
// for any given URL and all registered implementations will be consulted.
// Register is usually called in an implementation package's init method.
func Register(kind string, makefn func(Config) (Location, error), kindmatchfn func(*url.URL) bool, validatefn func(Config) error) {
	lock.Lock()
	defer lock.Unlock()
	// if already registered, leave
	if _, ok := locations[kind]; ok {
		return
	}
	locations[kind] = makefn
	configurations[kind] = validatefn
	kinds = append(kinds, kind)
	kindmatches = append(kindmatches, func(u *url.URL) string {
		if kindmatchfn(u) {
			return kind // match
		}
		return "" // empty string means no match
	})
}

// Dial gets a new Location with the given kind and
// configuration.
func Dial(kind string, config Config) (Location, error) {
	fn, ok := locations[kind]
	if !ok {
		return nil, errUnknownKind(kind)
	}
	return fn(config)
}

// Validate validates the config for a location
func Validate(kind string, config Config) error {
	fn, ok := configurations[kind]
	if !ok {
		return errUnknownKind(kind)
	}
	return fn(config)
}

// Kinds gets a list of installed location kinds.
func Kinds() []string {
	lock.RLock()
	defer lock.RUnlock()
	return kinds
}

// KindByURL gets the kind represented by the given URL.
// It consults all registered locations.
// Error returned if no match is found.
func KindByURL(u *url.URL) (string, error) {
	lock.RLock()
	defer lock.RUnlock()
	for _, fn := range kindmatches {
		kind := fn(u)
		if kind == "" {
			continue
		}
		return kind, nil
	}
	return "", errUnknownKind("")
}

// ConfigMap is a map[string]string that implements
// the Config method.
type ConfigMap map[string]string

// Config gets a string configuration value and a
// bool indicating whether the value was present or not.
func (c ConfigMap) Config(name string) (string, bool) {
	val, ok := c[name]
	return val, ok
}

// Set sets name configuration to value
func (c ConfigMap) Set(name, value string) {
	c[name] = value
}

// errUnknownKind indicates that a kind is unknown.
type errUnknownKind string

func (e errUnknownKind) Error() string {
	s := string(e)
	if len(s) > 0 {
		return "stow: unknown kind \"" + string(e) + "\""
	}
	return "stow: unknown kind"
}

type errNotSupported string

func (e errNotSupported) Error() string {
	return "not supported: " + string(e)
}

// IsNotSupported gets whether the error is due to
// a feature not being supported by a specific implementation.
func IsNotSupported(err error) bool {
	_, ok := err.(errNotSupported)
	return ok
}

// NotSupported gets an error describing the feature
// as not supported by this implementation.
func NotSupported(feature string) error {
	return errNotSupported(feature)
}
