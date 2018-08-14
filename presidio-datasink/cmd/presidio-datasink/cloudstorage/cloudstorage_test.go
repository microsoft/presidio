package cloudStorage

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestAddActionToFilePath(t *testing.T) {
	path := "/dir1/dir2/dir3/filename.txt"
	newp := addActionToFilePath(path, "action")
	assert.Equal(t, newp, "dir1/dir2/dir3/filename-action.txt")

	path = "/dir/file"
	newp = addActionToFilePath(path, "action")
	assert.Equal(t, newp, "dir/file-action")

	path = "file"
	newp = addActionToFilePath(path, "action")
	assert.Equal(t, newp, "file-action")
}
