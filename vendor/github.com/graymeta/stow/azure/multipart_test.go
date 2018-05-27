package azure

import (
	"crypto/md5"
	"fmt"
	"io"
	"os"
	"testing"

	"github.com/cheekybits/is"
	"github.com/graymeta/stow"
)

func TestChunkSize(t *testing.T) {
	is := is.New(t)

	// 10 bytes, should fit in a single chunk
	sz, err := determineChunkSize(10)
	is.NoErr(err)
	is.Equal(sz, startChunkSize)

	// Scale up the chunk size
	sz, err = determineChunkSize(maxParts*startChunkSize + 1)
	is.NoErr(err)
	is.Equal(sz, startChunkSize*2)

	// Maximum size
	sz, err = determineChunkSize(maxParts * maxChunkSize)
	is.NoErr(err)
	is.Equal(sz, maxChunkSize)

	// Add one byte, we shouldn't be able to upload this
	sz, err = determineChunkSize(maxParts*maxChunkSize + 1)
	is.Err(err)
	is.Equal(err, errMultiPartUploadTooBig)
}

func TestEncodeBlockID(t *testing.T) {
	is := is.New(t)

	is.Equal(encodedBlockID(10), "CgAAAAAAAAA=")
	is.Equal(encodedBlockID(600), "WAIAAAAAAAA=")
}

func TestMultipartUpload(t *testing.T) {
	is := is.New(t)

	if azureaccount == "" || azurekey == "" {
		t.Skip("skipping test because missing either AZUREACCOUNT or AZUREKEY")
	}
	cfg := stow.ConfigMap{"account": azureaccount, "key": azurekey}

	bigfile := os.Getenv("BIG_FILE_TO_UPLOAD")
	if bigfile == "" {
		t.Skip("skipping test because BIG_FILE_TO_UPLOAD was not set")
	}

	location, err := stow.Dial("azure", cfg)
	is.NoErr(err)
	is.OK(location)

	defer location.Close()

	cont, err := location.CreateContainer("bigfiletest")
	is.NoErr(err)
	is.OK(cont)

	defer func() {
		is.NoErr(location.RemoveContainer(cont.ID()))
	}()

	f, err := os.Open(bigfile)
	is.NoErr(err)
	defer f.Close()

	fi, err := f.Stat()
	is.NoErr(err)

	name := "bigfile/thebigfile"
	azc, ok := cont.(*container)
	is.OK(ok)
	is.NoErr(azc.multipartUpload(name, f, fi.Size()))

	item, err := cont.Item(name)
	is.NoErr(err)

	defer cont.RemoveItem(name)

	r, err := item.Open()
	is.NoErr(err)
	defer r.Close()

	hashNew := md5.New()
	_, err = io.Copy(hashNew, r)
	is.NoErr(err)

	f.Seek(0, 0)
	hashOld := md5.New()
	_, err = io.Copy(hashOld, f)
	is.NoErr(err)

	is.Equal(fmt.Sprintf("%x", hashOld.Sum(nil)), fmt.Sprintf("%x", hashNew.Sum(nil)))
}
