package scanner

import "github.com/presid-io/presidio/pkg/cache"

type WalkFunc func(item interface{})

type Scanner interface {
	Init()
	GetItemUniqueID(item interface{}) (string, error)
	GetItemContent(item interface{}) (string, error)
	GetItemPath(item interface{}) string
	IsContentSupported(item interface{}) error
	WalkItems(cache cache.Cache, fn WalkFunc) error
}
