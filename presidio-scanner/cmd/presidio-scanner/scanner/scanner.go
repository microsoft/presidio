package scanner

// WalkFunc is the function the is executed on the scanned item
type WalkFunc func(item interface{})

// Scanner interface represent the supported scanner methods.
type Scanner interface {
	//Init the scanner
	Init()

	//GetItemUniqueID returns the scanned item unique id
	GetItemUniqueID(item interface{}) (string, error)

	//GetItemContent returns the content of the scanned item
	GetItemContent(item interface{}) (string, error)

	//GetItemPath returns the item path
	GetItemPath(item interface{}) string

	//IsContentSupported returns if the item can be scanned.
	IsContentSupported(item interface{}) error

	//WalkItems walks over the items to scan and exectes WalkFunc on each of the items
	WalkItems(fn WalkFunc) error
}
