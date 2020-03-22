package cmd

import (
	"bytes"
	"io/ioutil"
	"net/http"
	"os"
	"os/exec"
	"strconv"
	"testing"

	"github.com/Microsoft/presidio/presctl/cmd/entities"
)

// clientMock is a mock for http client
type clientMock struct {
	returningCode int
}

// TestIsJson tests that the method differentiate between a valid to a non valid json string
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
	// This is a workaround, the idea is to start again the presctl but this time since we started
	// it we can check its exit code, hence verified the process got terminated with exception
	// (as expected)
	if os.Getenv("BE_CRASHER") == "1" {
		mockFail := &clientMock{returningCode: 400}
		entities.CreateTemplate(mockFail, "myproj", "anonymize", "template1", "template text")
		return
	}

	// re-run the presctl and expect to find an error exit code
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
	entities.CreateTemplate(mockSuccess, "myproj", "anonymize", "template1", "template text")

	mockSuccess = &clientMock{returningCode: http.StatusNoContent}
	entities.DeleteTemplate(mockSuccess, "myproj", "anonymize", "template1")

	mockSuccess = &clientMock{returningCode: http.StatusOK}
	entities.UpdateTemplate(mockSuccess, "myproj", "anonymize", "template1", "template text")

	entities.GetTemplate(mockSuccess, "myproj", "anonymize", "template1", "")
}

// TestRecognizersOperations tests that the positive flow of the templates commands is succesfull
func TestRecognizersOperations(t *testing.T) {
	mockSuccess := &clientMock{returningCode: http.StatusCreated}

	// verify all flows are ending with success
	entities.CreateRecognizer(mockSuccess, "myreco", "template text")

	mockSuccess = &clientMock{returningCode: http.StatusNoContent}
	entities.DeleteRecognizer(mockSuccess, "myreco")

	mockSuccess = &clientMock{returningCode: http.StatusOK}
	entities.UpdateRecognizer(mockSuccess, "myreco", "template text")

	entities.GetRecognizer(mockSuccess, "myreco", "")
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
