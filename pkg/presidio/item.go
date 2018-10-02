package presidio

// Item interface represent the supported item's methods.
type Item interface {

	//GetUniqueID returns the scanned item unique id
	GetUniqueID() (string, error)

	//GetContent returns the content of the scanned item
	GetContent() (string, error)

	//GetPath returns the item path
	GetPath() string

	//IsContentTypeSupported returns if the item can be scanned.
	IsContentTypeSupported() error
}
