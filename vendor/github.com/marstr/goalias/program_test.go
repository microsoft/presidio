package main

import (
	"errors"
	"testing"
)

func Test_getAliasPath(t *testing.T) {
	paths := []struct {
		raw      string
		expected string
	}{
		{
			"github.com/Azure/azure-sdk-for-go/service/resources/management/2016-09-01-preview/managedapplications",
			"github.com/Azure/azure-sdk-for-go/profile/example/resources/management/managedapplications",
		},
		{
			`github.com/Azure/azure-sdk-for-go/service/cdn/management/2016-10-02/cdn`,
			"github.com/Azure/azure-sdk-for-go/profile/example/cdn/management/cdn",
		},
	}

	for _, tc := range paths {
		t.Run("", func(t *testing.T) {
			if result, err := getAliasPath(tc.raw, "example"); err != nil {
				t.Error(err)
			} else if result != tc.expected {
				t.Logf("\ngot: \t%s\nwant:\t%s", result, tc.expected)
				t.Fail()
			}
		})
	}
}

func Test_Invalid_getAliasPath(t *testing.T) {
	paths := []struct {
		raw      string
		expected error
	}{
		{ // Missing prefix "github.com/Azure/azure-sdk-for-go/arm"
			"resources/managedapplications/2016-09-01-preview/managedapplications",
			errors.New("path does not resemble a known package path"),
		},
	}

	for _, tc := range paths {
		t.Run("", func(t *testing.T) {
			result, err := getAliasPath(tc.raw, "example")

			if err == nil {
				t.Log("no error was encountered")
				t.Fail()
			} else if actual, wanted := err.Error(), tc.expected.Error(); actual != wanted {
				t.Logf("\ngot: \t%s\nwant:\t%s", actual, wanted)
				t.Fail()
			}

			if result != "" {
				t.Log("result should have been \"\"")
				t.Fail()
			}
		})
	}
}
