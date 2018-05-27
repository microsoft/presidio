package google

import (
	"io/ioutil"
	"os"
	"reflect"
	"testing"

	"github.com/cheekybits/is"
	"github.com/graymeta/stow"
	"github.com/graymeta/stow/test"
)

func TestStow(t *testing.T) {

	credFile := os.Getenv("GOOGLE_CREDENTIALS_FILE")
	projectId := os.Getenv("GOOGLE_PROJECT_ID")

	if credFile == "" || projectId == "" {
		t.Skip("skipping test because GOOGLE_CREDENTIALS_FILE or GOOGLE_PROJECT_ID not set.")
	}

	b, err := ioutil.ReadFile(credFile)
	if err != nil {
		t.Fatal(err)
	}

	config := stow.ConfigMap{
		"json":       string(b),
		"project_id": projectId,
	}
	test.All(t, "google", config)
}

func TestPrepMetadataSuccess(t *testing.T) {
	is := is.New(t)

	m := make(map[string]string)
	m["one"] = "two"
	m["3"] = "4"
	m["ninety-nine"] = "100"

	m2 := make(map[string]interface{})
	for key, value := range m {
		m2[key] = value
	}

	//returns map[string]interface
	returnedMap, err := prepMetadata(m2)
	is.NoErr(err)

	if !reflect.DeepEqual(returnedMap, m) {
		t.Errorf("Expected map (%+v) and returned map (%+v) are not equal.", m, returnedMap)
	}
}

func TestPrepMetadataFailureWithNonStringValues(t *testing.T) {
	is := is.New(t)

	m := make(map[string]interface{})
	m["float"] = 8.9
	m["number"] = 9

	_, err := prepMetadata(m)
	is.Err(err)
}
