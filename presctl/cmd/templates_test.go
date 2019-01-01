package cmd

import (
	"bytes"
	"io/ioutil"
	"net/http"
	"os"
	"os/exec"
	"strconv"
	"testing"
)

// clientMock is a mock for http client
type clientMock struct {
	returningCode int
}

// TestIsJson tests that the method diffrentiate between a valid to a non valid json string
func TestIsJson(t *testing.T) {
	nonJSONStr := "A simple string"
	if isJSON(nonJSONStr) {
		t.Fatal("isJson failed. the given string is not a valid JSON, yet the method returned true")
	}

	nonJSONStr = `{
	                itemA: "A"
                  }`
	if isJSON(nonJSONStr) {
		t.Fatal("isJson failed. the given string is not a valid JSON, yet the method returned true")
	}

	validJSONStr := `{
	            	  "itemA": "A"
                     }`
	if !isJSON(validJSONStr) {
		t.Fatal("isJson failed. the given is a valid JSON, yet the method returned false")
	}
}

// TestFailingCreateTemplate tests that when presidio returns an invalid status code the cli exists with an error
func TestFailingCreateTemplate(t *testing.T) {
	// we expect the exit code to be 1, if the returned status code is not as expected (not 201)
	if os.Getenv("BE_CRASHER") == "1" {
		mockFail := &clientMock{returningCode: 400}
		createTemplate(mockFail, "myproj", "anonymize", "template1", "template text")
		return
	}
	cmd := exec.Command(os.Args[0], "-test.run=TestFailingCreateTemplate")
	cmd.Env = append(os.Environ(), "BE_CRASHER=1")
	err := cmd.Run()
	e, ok := err.(*exec.ExitError)
	if ok && e.Success() {
		t.Fatalf("process ran with err %v, want exit status 1", err)
	}
}

// TestTemplatesOperations tests that the positive flow of the templates commands is succesfull
func TestTemplatesOperations(t *testing.T) {
	mockSuccess := &clientMock{returningCode: http.StatusCreated}

	// verify all flows are ending with success
	createTemplate(mockSuccess, "myproj", "anonymize", "template1", "template text")

	mockSuccess = &clientMock{returningCode: http.StatusNoContent}
	deleteTemplate(mockSuccess, "myproj", "anonymize", "template1")

	mockSuccess = &clientMock{returningCode: http.StatusOK}
	updateTemplate(mockSuccess, "myproj", "anonymize", "template1", "template text")
	getTemplate(mockSuccess, "myproj", "anonymize", "template1", "")
}

func (c *clientMock) Do(req *http.Request) (*http.Response, error) {
	fakeMsg := "{ \"text\": \"Fake response....\" }"

	// we quote the msg to follow the convention of the presidio server
	quotedFakeMsg := strconv.Quote(fakeMsg)
	fakeStringResponseBody := []byte(quotedFakeMsg)
	return &http.Response{StatusCode: c.returningCode,
		Body:          ioutil.NopCloser(bytes.NewReader(fakeStringResponseBody)),
		ContentLength: int64(len(fakeStringResponseBody))}, nil
}
