package azure

import (
	"fmt"
	"os"
	"reflect"
	"testing"

	"github.com/cheekybits/is"
	"github.com/graymeta/stow"
	"github.com/graymeta/stow/test"
)

var (
	azureaccount = os.Getenv("AZUREACCOUNT")
	azurekey     = os.Getenv("AZUREKEY")
)

func TestStow(t *testing.T) {
	if azureaccount == "" || azurekey == "" {
		t.Skip("skipping test because missing either AZUREACCOUNT or AZUREKEY")
	}

	cfg := stow.ConfigMap{"account": azureaccount, "key": azurekey}
	test.All(t, "azure", cfg)
}

func TestEtagCleanup(t *testing.T) {
	etagValue := "9c51403a2255f766891a1382288dece4"
	permutations := []string{
		`"%s"`,       // Enclosing quotations
		`W/\"%s\"`,   // Weak tag identifier with escapted quotes
		`W/"%s"`,     // Weak tag identifier with quotes
		`"\"%s"\"`,   // Double quotes, inner escaped
		`""%s""`,     // Double quotes,
		`"W/"%s""`,   // Double quotes with weak identifier
		`"W/\"%s\""`, // Double quotes with weak identifier, inner escaped
	}
	for index, p := range permutations {
		testStr := fmt.Sprintf(p, etagValue)
		cleanTestStr := cleanEtag(testStr)
		if etagValue != cleanTestStr {
			t.Errorf(`Failure at permutation #%d (%s), result: %s`,
				index, permutations[index], cleanTestStr)
		}
	}
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
