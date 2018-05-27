package local

import (
	"fmt"
	"os"
	"path/filepath"
	"syscall"
	"time"
)

func getFileMetadata(path string, info os.FileInfo) map[string]interface{} {
	hardlink, symlink, linkTarget := false, false, ""
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
		MetadataSize:       info.Size(),
		MetadataIsSymlink:  symlink,
		MetadataIsHardlink: hardlink,
		MetadataLink:       linkTarget,
	}

	if stat := info.Sys().(*syscall.Win32FileAttributeData); stat != nil {
		m["atime"] = time.Unix(0, stat.LastAccessTime.Nanoseconds()).Format(time.RFC3339Nano)
		m["mtime"] = time.Unix(0, stat.LastWriteTime.Nanoseconds()).Format(time.RFC3339Nano)
	}

	ext := filepath.Ext(info.Name())
	if len(ext) > 0 {
		m["ext"] = ext
	}

	return m
}
