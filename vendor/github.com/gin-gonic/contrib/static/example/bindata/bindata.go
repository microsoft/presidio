package main

import (
	"bytes"
	"compress/gzip"
	"fmt"
	"io"
	"os"
	"strings"
)

func bindata_read(data []byte, name string) ([]byte, error) {
	gz, err := gzip.NewReader(bytes.NewBuffer(data))
	if err != nil {
		return nil, fmt.Errorf("Read %q: %v", name, err)
	}

	var buf bytes.Buffer
	_, err = io.Copy(&buf, gz)
	gz.Close()

	if err != nil {
		return nil, fmt.Errorf("Read %q: %v", name, err)
	}

	return buf.Bytes(), nil
}

func data_index_html() ([]byte, error) {
	return bindata_read([]byte{
		0x1f, 0x8b, 0x08, 0x00, 0x00, 0x09, 0x6e, 0x88, 0x00, 0xff, 0x44, 0xce,
		0xbd, 0xae, 0xc2, 0x30, 0x0c, 0x05, 0xe0, 0xbd, 0x4f, 0xe1, 0x9b, 0xbd,
		0xaa, 0xba, 0xdd, 0x21, 0xcd, 0xc2, 0xef, 0x06, 0x43, 0x19, 0x18, 0x5d,
		0x62, 0x35, 0x41, 0x4e, 0x22, 0x15, 0x4b, 0x88, 0xb7, 0x27, 0x21, 0x45,
		0x4c, 0x39, 0xb1, 0xf5, 0x1d, 0x59, 0xff, 0x6d, 0x4f, 0x9b, 0xf1, 0x7a,
		0xde, 0x81, 0x93, 0xc0, 0xa6, 0xd1, 0xe5, 0x01, 0xc6, 0x38, 0x0f, 0xea,
		0x8e, 0xca, 0x34, 0x00, 0xda, 0x11, 0xda, 0x12, 0x72, 0x0c, 0x24, 0x08,
		0x37, 0x87, 0xcb, 0x83, 0x64, 0x50, 0x97, 0x71, 0xdf, 0xfe, 0x2b, 0xe8,
		0xd6, 0xa5, 0x78, 0x61, 0x32, 0x73, 0x6a, 0x27, 0x1f, 0x2d, 0x0a, 0xea,
		0xae, 0x4e, 0x4a, 0x47, 0xf7, 0x2d, 0xd1, 0x53, 0xb2, 0xaf, 0x15, 0xb8,
		0xde, 0x1c, 0x89, 0x39, 0xc1, 0xc1, 0x47, 0xf8, 0x39, 0x08, 0xde, 0x5a,
		0xa6, 0x27, 0x2e, 0x94, 0x5d, 0x5f, 0x7d, 0x65, 0xf9, 0xff, 0x39, 0xf3,
		0x1d, 0x00, 0x00, 0xff, 0xff, 0x51, 0x69, 0x85, 0x27, 0xb7, 0x00, 0x00,
		0x00,
	},
		"data/index.html",
	)
}

// Asset loads and returns the asset for the given name.
// It returns an error if the asset could not be found or
// could not be loaded.
func Asset(name string) ([]byte, error) {
	cannonicalName := strings.Replace(name, "\\", "/", -1)
	if f, ok := _bindata[cannonicalName]; ok {
		return f()
	}
	return nil, fmt.Errorf("Asset %s not found", name)
}

// AssetNames returns the names of the assets.
func AssetNames() []string {
	names := make([]string, 0, len(_bindata))
	for name := range _bindata {
		names = append(names, name)
	}
	return names
}

// _bindata is a table, holding each asset generator, mapped to its name.
var _bindata = map[string]func() ([]byte, error){
	"data/index.html": data_index_html,
}

// AssetDir returns the file names below a certain
// directory embedded in the file by go-bindata.
// For example if you run go-bindata on data/... and data contains the
// following hierarchy:
//     data/
//       foo.txt
//       img/
//         a.png
//         b.png
// then AssetDir("data") would return []string{"foo.txt", "img"}
// AssetDir("data/img") would return []string{"a.png", "b.png"}
// AssetDir("foo.txt") and AssetDir("notexist") would return an error
func AssetDir(name string) ([]string, error) {
	cannonicalName := strings.Replace(name, "\\", "/", -1)
	pathList := strings.Split(cannonicalName, "/")
	node := _bintree
	for _, p := range pathList {
		node = node.Children[p]
		if node == nil {
			return nil, fmt.Errorf("Asset %s not found", name)
		}
	}
	if node.Func != nil {
		return nil, fmt.Errorf("Asset %s not found", name)
	}
	rv := make([]string, 0, len(node.Children))
	for name := range node.Children {
		rv = append(rv, name)
	}
	return rv, nil
}

type _bintree_t struct {
	Func     func() ([]byte, error)
	Children map[string]*_bintree_t
}

var _bintree = &_bintree_t{nil, map[string]*_bintree_t{
	"data": &_bintree_t{nil, map[string]*_bintree_t{
		"index.html": &_bintree_t{data_index_html, map[string]*_bintree_t{}},
	}},
}}

// AssetInfo returns file info of given path
func AssetInfo(path string) (os.FileInfo, error) {
	return os.Stat(path)
}
