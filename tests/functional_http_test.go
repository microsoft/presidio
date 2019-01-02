// +build functional

package tests

import (
	"bytes"
	"io"
	"io/ioutil"
	"mime/multipart"
	"net/http"
	"net/url"
	"os"
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"
)

func generatePayload(name string) []byte {
	payload, err := ioutil.ReadFile("./testdata/" + name)
	if err != nil {
		panic(err)
	}
	return payload
}

func invokeHTTPRequest(t *testing.T, path string, method string, payload []byte) string {

	request := &http.Request{
		Method: method,
		URL:    &url.URL{Scheme: "http", Host: "localhost:8080", Path: path},
		Body:   ioutil.NopCloser(bytes.NewReader(payload)),
		Header: http.Header{
			"Content-Type": []string{"application/json"},
		},
	}

	resp, err := http.DefaultClient.Do(request)
	assert.NoError(t, err)

	if resp.StatusCode >= 300 {
		t.Errorf("%s %s: expected status code smaller than 300 , got '%d'\n", request.Method, request.URL.String(), resp.StatusCode)
	}
	defer resp.Body.Close()
	bodyBytes, _ := ioutil.ReadAll(resp.Body)
	return string(bodyBytes)
}

func invokeHTTPUpload(t *testing.T, path string, values map[string]io.Reader) []byte {

	var b bytes.Buffer
	w := multipart.NewWriter(&b)
	for key, r := range values {
		var fw io.Writer
		var err error
		if x, ok := r.(io.Closer); ok {
			defer x.Close()
		}
		// Add an image file
		if x, ok := r.(*os.File); ok {
			fw, err = w.CreateFormFile(key, x.Name())
			assert.NoError(t, err)

		} else {
			// Add other fields
			fw, err = w.CreateFormField(key)
			assert.NoError(t, err)

		}
		_, err = io.Copy(fw, r)
		assert.NoError(t, err)

	}

	w.Close()

	req, err := http.NewRequest("POST", "http://localhost:8080"+path, &b)
	assert.NoError(t, err)
	req.Header.Set("Content-Type", w.FormDataContentType())

	res, err := http.DefaultClient.Do(req)
	assert.NoError(t, err)

	if res.StatusCode != http.StatusOK {
		t.Errorf("bad status: %s", res.Status)
	}
	defer res.Body.Close()
	bodyBytes, _ := ioutil.ReadAll(res.Body)
	return bodyBytes
}

func TestAddTemplate(t *testing.T) {
	payload := generatePayload("analyze-template.json")
	invokeHTTPRequest(t, "/api/v1/templates/test/analyze/test", "POST", payload)

	payload = generatePayload("anonymize-template.json")
	invokeHTTPRequest(t, "/api/v1/templates/test/anonymize/test", "POST", payload)
}

func TestDeleteTemplate(t *testing.T) {
	invokeHTTPRequest(t, "/api/v1/templates/test/analyze/test", "DELETE", []byte(""))
	invokeHTTPRequest(t, "/api/v1/templates/test/anonymize/test", "DELETE", []byte(""))
}

func TestAnalyzer(t *testing.T) {
	TestAddTemplate(t)
	payload := generatePayload("analyze-request.json")
	invokeHTTPRequest(t, "/api/v1/projects/test/analyze", "POST", payload)
}

func TestAnonymizer(t *testing.T) {
	TestAddTemplate(t)
	payload := generatePayload("anonymize-request.json")
	invokeHTTPRequest(t, "/api/v1/projects/test/anonymize", "POST", payload)
}

func TestImageAnonymizer(t *testing.T) {

	file, err := os.Open("./testdata/ocr-test.png")
	assert.NoError(t, err)

	payload := map[string]io.Reader{
		"data":                   file,
		"analyzeTemplate":        strings.NewReader((string)(generatePayload("analyze-image-template.json"))),
		"anonymizeImageTemplate": strings.NewReader((string)(generatePayload("anonymize-image-template.json"))),
		"imageType":              strings.NewReader("image/png"),
		"detectionType":          strings.NewReader("OCR"),
	}

	result := invokeHTTPUpload(t, "/api/v1/projects/test/anonymize-image", payload)
	savedOutputImage, err := ioutil.ReadFile("./testdata/ocr-output.png")
	assert.NoError(t, err)

	assert.Equal(t, len(savedOutputImage), len(result))

}
