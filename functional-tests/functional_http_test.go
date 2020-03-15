// +build functional

package tests

import (
	"io"
	"io/ioutil"
	"os"
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"

	"github.com/Microsoft/presidio/functional-tests/common"
)

func TestAddTemplate(t *testing.T) {
	payload := common.GeneratePayload("analyze-template.json")
	common.InvokeHTTPRequest(t, "/api/v1/templates/test/analyze/test", "POST", payload)

	payload = common.GeneratePayload("anonymize-template.json")
	common.InvokeHTTPRequest(t, "/api/v1/templates/test/anonymize/test", "POST", payload)
}

func TestDeleteTemplate(t *testing.T) {
	common.InvokeHTTPRequest(t, "/api/v1/templates/test/analyze/test", "DELETE", []byte(""))
	common.InvokeHTTPRequest(t, "/api/v1/templates/test/anonymize/test", "DELETE", []byte(""))
}

func TestAnalyzer(t *testing.T) {
	TestAddTemplate(t)
	payload := common.GeneratePayload("analyze-request.json")
	common.InvokeHTTPRequest(t, "/api/v1/projects/test/analyze", "POST", payload)
}

func TestAnonymizer(t *testing.T) {
	TestAddTemplate(t)
	payload := common.GeneratePayload("anonymize-request.json")
	common.InvokeHTTPRequest(t, "/api/v1/projects/test/anonymize", "POST", payload)
}

func TestImageAnonymizer(t *testing.T) {

	file, err := os.Open(common.TestDataPath + "ocr-test.png")
	assert.NoError(t, err)

	payload := map[string]io.Reader{
		"file":                   file,
		"analyzeTemplate":        strings.NewReader((string)(common.GeneratePayload("analyze-image-template.json"))),
		"anonymizeImageTemplate": strings.NewReader((string)(common.GeneratePayload("anonymize-image-template.json"))),
		"imageType":              strings.NewReader("image/png"),
		"detectionType":          strings.NewReader("OCR"),
	}

	result := common.InvokeHTTPUpload(t, "/api/v1/projects/test/anonymize-image", payload)
	savedOutputImage, err := ioutil.ReadFile(common.TestDataPath + "ocr-result.png")
	assert.NoError(t, err)

	assert.Equal(t, len(savedOutputImage), len(result))

}
