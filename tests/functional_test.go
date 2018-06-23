// +build functional

package tests

import (
	"bytes"
	"io/ioutil"
	"net/http"
	"net/url"
	"testing"
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
	if err != nil {
		t.Error(err)
	}
	if resp.StatusCode >= 300 {
		t.Errorf("%s %s: expected status code smaller than 300 , got '%d'\n", request.Method, request.URL.String(), resp.StatusCode)
	}
	defer resp.Body.Close()
	bodyBytes, _ := ioutil.ReadAll(resp.Body)
	return string(bodyBytes)
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
