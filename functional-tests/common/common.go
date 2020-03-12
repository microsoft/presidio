package common

import (
	"bytes"
	"io"
	"io/ioutil"
	"mime/multipart"
	"net/http"
	"net/url"
	"os"
	"testing"

	"github.com/stretchr/testify/assert"
)

// TestDataPath test data path
const TestDataPath string = "../presidio-tester/cmd/presidio-tester/testdata/"
const host = "localhost:8080"

//GeneratePayload generate payload
func GeneratePayload(name string) []byte {
	payload, err := ioutil.ReadFile(TestDataPath + name)
	if err != nil {
		panic(err)
	}
	return payload
}

//InvokeHTTPRequest invoke http request
func InvokeHTTPRequest(t *testing.T, path string, method string, payload []byte) string {

	request := &http.Request{
		Method: method,
		URL:    &url.URL{Scheme: "http", Host: host, Path: path},
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

//InvokeHTTPUpload invoke upload
func InvokeHTTPUpload(t *testing.T, path string, values map[string]io.Reader) []byte {

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

	req, err := http.NewRequest("POST", "http://"+host+path, &b)
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
