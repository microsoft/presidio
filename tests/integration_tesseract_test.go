// +build integration

package tests

import (
	"io/ioutil"
	"testing"

	"encoding/json"

	"github.com/stretchr/testify/assert"

	types "github.com/Microsoft/presidio-genproto/golang"
	"github.com/Microsoft/presidio/presidio-ocr/cmd/presidio-ocr/ocr"
)

func TestOCR(t *testing.T) {

	content, err := ioutil.ReadFile("./testdata/ocr-test.png")
	assert.NoError(t, err)

	image := &types.Image{
		Data: content,
	}
	result, err := ocr.PerformOCR(image)

	assert.NoError(t, err)
	assert.NotEqual(t, "", result.Text)

	savedJSONResult, err := ioutil.ReadFile("./testdata/ocr-result.json")
	assert.NoError(t, err)
	jsonResult, _ := json.Marshal(result)
	assert.Equal(t, savedJSONResult, jsonResult)

}
