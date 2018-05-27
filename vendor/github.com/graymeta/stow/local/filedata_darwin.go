package local

import (
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"syscall"
	"time"
)

func getFileMetadata(path string, info os.FileInfo) map[string]interface{} {

	hardlink := false
	symlink := false
	var linkTarget string
	var inodedata interface{}
	if inode, err := getInodeinfo(info); err != nil {
		inodedata = map[string]interface{}{"error": err.Error()}
	} else {
		inodedata = inode
		if inode.NLink > 1 {
			hardlink = true
		}
	}
	if info.Mode()&os.ModeSymlink == os.ModeSymlink {
		symlink = true
		linkTarget, _ = os.Readlink(path)
	}
	m := map[string]interface{}{
		MetadataPath:       filepath.Clean(path),
		MetadataIsDir:      info.IsDir(),
		MetadataDir:        filepath.Dir(path),
		MetadataName:       info.Name(),
		MetadataMode:       fmt.Sprintf("%o", info.Mode()),
		MetadataModeD:      fmt.Sprintf("%v", uint32(info.Mode())),
		MetadataPerm:       info.Mode().String(),
		MetadataINode:      inodedata,
		MetadataSize:       info.Size(),
		MetadataIsHardlink: hardlink,
		MetadataIsSymlink:  symlink,
		MetadataLink:       linkTarget,
	}

	if stat := info.Sys().(*syscall.Stat_t); stat != nil {
		m["atime"] = time.Unix(int64(stat.Atimespec.Sec), int64(stat.Atimespec.Nsec)).Format(time.RFC3339Nano)
		m["mtime"] = time.Unix(int64(stat.Mtimespec.Sec), int64(stat.Mtimespec.Nsec)).Format(time.RFC3339Nano)
		m["uid"] = stat.Uid
		m["gid"] = stat.Gid
	}

	ext := filepath.Ext(info.Name())
	if len(ext) > 0 {
		m["ext"] = ext
	}

	return m
}

type inodeinfo struct {
	// NLink is the number of times this file is linked to by
	// hardlinks.
	NLink uint16
	// Ino is the inode number for the file.
	Ino uint64
}

func getInodeinfo(fi os.FileInfo) (*inodeinfo, error) {
	var statT *syscall.Stat_t
	var ok bool
	if statT, ok = fi.Sys().(*syscall.Stat_t); !ok {
		return nil, errors.New("unable to determine if file is a hardlink (expected syscall.Stat_t)")
	}
	return &inodeinfo{
		Ino:   statT.Ino,
		NLink: uint16(statT.Nlink),
	}, nil
}
