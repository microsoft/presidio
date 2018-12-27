package cmd

import (
	"net/http"
	"os"
	"os/exec"
	"testing"
)

type FailingClientMock struct {
}

type ClientMock struct {
	returningCode int
}

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
	if isJSON(validJSONStr) == false {
		t.Fatal("isJson failed. the given is a valid JSON, yet the method returned false")
	}
}

func TestFailingCreateTemplate(t *testing.T) {
	// we expect the exit code to be 1, if the returned status code is not as expected (not 201)
	if os.Getenv("BE_CRASHER") == "1" {
		mockFail := &ClientMock{returningCode: 400}
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

func TestTemplatesOperations(t *testing.T) {
	mockSuccess := &ClientMock{returningCode: http.StatusCreated}

	// verify all flows are ending with success
	createTemplate(mockSuccess, "myproj", "anonymize", "template1", "template text")

	mockSuccess = &ClientMock{returningCode: http.StatusNoContent}
	deleteTemplate(mockSuccess, "myproj", "anonymize", "template1")

	mockSuccess = &ClientMock{returningCode: http.StatusOK}
	updateTemplate(mockSuccess, "myproj", "anonymize", "template1", "template text")
	//getTemplate(mockSuccess, "myproj", "anonymize", "template1", "/tmp/tests")
}

func (c *ClientMock) Do(req *http.Request) (*http.Response, error) {
	return &http.Response{StatusCode: c.returningCode}, nil
}
