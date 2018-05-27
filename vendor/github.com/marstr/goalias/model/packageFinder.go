package model

import (
	"errors"
	"go/parser"
	"go/token"
	"os"
	"path/filepath"

	"github.com/marstr/collection"
)

// PackageFinder traverses a directory looking for Go Packages that could be aliased.
type PackageFinder struct {
	root string
}

// NewPackageFinder creates a new instance of PackageFinder with an initialized value of `Root`.
func NewPackageFinder(root string) *PackageFinder {
	return &PackageFinder{
		root: root,
	}
}

// Root fetches the value that a PackageFinder will begin searching in.
func (finder PackageFinder) Root() string {
	if finder.root == "" {
		return os.Getenv("GOPATH")
	}
	return finder.root
}

// SetRoot sets the value that a PackageFInder should use for its search.
func (finder *PackageFinder) SetRoot(val string) {
	finder.root = val
}

// Enumerate traverses a directory parsing aliasable packages. The type passed to the channel is `string` which are paths to directories containing a parsable go package.
func (finder PackageFinder) Enumerate(cancel <-chan struct{}) collection.Enumerator {
	results := make(chan interface{})
	go func() {
		defer close(results)

		filepath.Walk(finder.Root(), func(localPath string, info os.FileInfo, openErr error) (err error) {
			if !info.IsDir() || openErr != nil {
				return
			}
			if info.Name() == "vendor" {
				err = filepath.SkipDir
				return
			}

			files := &token.FileSet{}

			if pkgs, parseErr := parser.ParseDir(files, localPath, nil, 0); parseErr != nil || len(pkgs) < 1 {
				return
			}

			select {
			case results <- localPath:
				// Intentionally Left Blank
			case <-cancel:
				err = errors.New("enumeration cancelled")
				return
			}

			return
		})
	}()
	return results
}
