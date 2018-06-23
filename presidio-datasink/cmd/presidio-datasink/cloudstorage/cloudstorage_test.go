package cloudStorage

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestAddSuffixToPath(t *testing.T) {
	path := "/dir1/dir2/dir3/filename.txt"
	newPath := addSuffixToPath(path, "action")
	assert.Equal(t, newPath, "dir1/dir2/dir3/filename-action.txt")

	path = "/dir/file"
	newPath = addSuffixToPath(path, "action")
	assert.Equal(t, newPath, "dir/file-action")

	path = "file"
	newPath = addSuffixToPath(path, "action")
	assert.Equal(t, newPath, "file-action")
}
