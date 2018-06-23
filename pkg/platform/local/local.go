package local

import (
	"fmt"

	"github.com/Microsoft/presidio/pkg/platform"
)

// store represents a storage engine for a brigade.Project.
type store struct {
	path string
}

// New initializes a new storage backend.
func New(path string) (platform.Store, error) {

	if path == "" {
		return nil, fmt.Errorf("local path cannot be empty")
	}
	return &store{
		path: path,
	}, nil
}
