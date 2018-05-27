package azure

import (
	"encoding/base64"
	"encoding/binary"
	"errors"
	"io"

	az "github.com/Azure/azure-sdk-for-go/storage"
)

// constants related to multi-part uploads
const (
	startChunkSize = 4 * 1024 * 1024
	maxChunkSize   = 100 * 1024 * 1024
	maxParts       = 50000
)

// errMultiPartUploadTooBig is the error returned when a file is just too big to upload
var errMultiPartUploadTooBig = errors.New("size exceeds maximum capacity for a single multi-part upload")

// encodedBlockID returns the base64 encoded block id as expected by azure
func encodedBlockID(id uint64) string {
	bytesID := make([]byte, 8)
	binary.LittleEndian.PutUint64(bytesID, id)
	return base64.StdEncoding.EncodeToString(bytesID)
}

// determineChunkSize determines the chunk size for a multi-part upload.
func determineChunkSize(size int64) (int64, error) {
	var chunkSize = int64(startChunkSize)

	for {
		parts := size / chunkSize
		rem := size % chunkSize

		if rem != 0 {
			parts++
		}

		if parts <= maxParts {
			break
		}

		if chunkSize == maxChunkSize {
			return 0, errMultiPartUploadTooBig
		}

		chunkSize *= 2
		if chunkSize > maxChunkSize {
			chunkSize = maxChunkSize
		}
	}

	return chunkSize, nil
}

// multipartUpload performs a multi-part upload by chunking the data, putting each chunk, then
// assembling the chunks into a blob
func (c *container) multipartUpload(name string, r io.Reader, size int64) error {
	chunkSize, err := determineChunkSize(size)
	if err != nil {
		return err
	}
	var buf = make([]byte, chunkSize)

	var blocks []az.Block
	var rawID uint64
	blob := c.client.GetContainerReference(c.id).GetBlobReference(name)

	// TODO: upload the parts in parallel
	for {
		n, err := r.Read(buf)
		if err != nil {
			if err == io.EOF {
				break
			}
			return err
		}

		blockID := encodedBlockID(rawID)
		chunk := buf[:n]

		if err := blob.PutBlock(blockID, chunk, nil); err != nil {
			return err
		}

		blocks = append(blocks, az.Block{
			ID:     blockID,
			Status: az.BlockStatusLatest,
		})
		rawID++
	}

	return blob.PutBlockList(blocks, nil)
}
