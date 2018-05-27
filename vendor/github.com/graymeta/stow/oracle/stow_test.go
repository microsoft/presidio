package swift

import (
	"errors"
	"net/http"
	"os"
	"reflect"
	"testing"

	"github.com/cheekybits/is"
	"github.com/graymeta/stow"
	"github.com/graymeta/stow/test"
)

var cfgUnmetered = stow.ConfigMap{
	"username":               os.Getenv("SWIFTUNMETEREDUSERNAME"),
	"password":               os.Getenv("SWIFTUNMETEREDPASSWORD"),
	"authorization_endpoint": os.Getenv("SWIFTUNMETEREDAUTHENDPOINT"),
}

var cfgMetered = stow.ConfigMap{
	"username":               os.Getenv("SWIFTMETEREDUSERNAME"),
	"password":               os.Getenv("SWIFTMETEREDPASSWORD"),
	"authorization_endpoint": os.Getenv("SWIFTMETEREDAUTHENDPOINT"),
}

func checkCredentials(config stow.Config) error {
	v, ok := config.Config(ConfigUsername)
	if !ok || v == "" {
		return errors.New("missing account username")
	}

	v, ok = config.Config(ConfigPassword)
	if !ok || v == "" {
		return errors.New("missing account password")
	}

	v, ok = config.Config(ConfigAuthEndpoint)
	if !ok || v == "" {
		return errors.New("missing authorization endpoint")
	}

	return nil
}

func TestStowMetered(t *testing.T) {
	err := checkCredentials(cfgMetered)
	if err != nil {
		t.Skip("skipping test because " + err.Error())
	}
	test.All(t, "oracle", cfgMetered)
}

func TestStowUnMetered(t *testing.T) {
	err := checkCredentials(cfgUnmetered)
	if err != nil {
		t.Skip("skipping test because " + err.Error())
	}
	test.All(t, "oracle", cfgUnmetered)
}

func TestGetItemUTCLastModified(t *testing.T) {
	err := checkCredentials(cfgMetered)
	if err != nil {
		t.Skip("skipping test because " + err.Error())
	}

	tr := http.DefaultTransport
	http.DefaultTransport = &bogusLastModifiedTransport{tr}
	defer func() {
		http.DefaultTransport = tr
	}()

	test.All(t, "oracle", cfgMetered)
}

type bogusLastModifiedTransport struct {
	http.RoundTripper
}

func (t *bogusLastModifiedTransport) RoundTrip(r *http.Request) (*http.Response, error) {
	res, err := t.RoundTripper.RoundTrip(r)
	if err != nil {
		return res, err
	}
	res.Header.Set("Last-Modified", "Tue, 23 Aug 2016 15:12:44 UTC")
	return res, err
}

func (t *bogusLastModifiedTransport) CloseIdleConnections() {
	if tr, ok := t.RoundTripper.(interface {
		CloseIdleConnections()
	}); ok {
		tr.CloseIdleConnections()
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

	assertionM := make(map[string]string)
	assertionM["X-Object-Meta-one"] = "two"
	assertionM["X-Object-Meta-3"] = "4"
	assertionM["X-Object-Meta-ninety-nine"] = "100"

	//returns map[string]interface
	returnedMap, err := prepMetadata(m2)
	is.NoErr(err)

	if !reflect.DeepEqual(returnedMap, assertionM) {
		t.Errorf("Expected map (%+v) and returned map (%+v) are not equal.", assertionM, returnedMap)
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
