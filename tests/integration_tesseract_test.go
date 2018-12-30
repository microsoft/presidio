// +build functional

package tests

import (
	"io/ioutil"
	"testing"

	//"encoding/json"
	"github.com/otiai10/gosseract"
	"github.com/stretchr/testify/assert"

	types "github.com/Microsoft/presidio-genproto/golang"
	"github.com/Microsoft/presidio/presidio-ocr/cmd/presidio-ocr/ocr"
)

func TestOCR(t *testing.T) {

	client := gosseract.NewClient()
	defer client.Close()

	content, err := ioutil.ReadFile("./testdata/ocr-test.png")
	assert.NoError(t, err)

	image := &types.Image{
		Data: content,
	}
	result, err := ocr.PerformOCR(client, image)

	assert.NoError(t, err)
	assert.NotEqual(t, "", result.Text)

	//	b, _ := json.Marshal(result)
	//	ioutil.WriteFile("test.json", b, 0777)

}
