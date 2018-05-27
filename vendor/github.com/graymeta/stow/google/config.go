package google

import (
	"errors"
	"net/http"
	"net/url"
	"strings"

	"golang.org/x/net/context"
	"golang.org/x/oauth2"
	"golang.org/x/oauth2/google"
	storage "google.golang.org/api/storage/v1"

	"github.com/graymeta/stow"
)

// Kind represents the name of the location/storage type.
const Kind = "google"

const (
	// The service account json blob
	ConfigJSON      = "json"
	ConfigProjectId = "project_id"
	ConfigScopes    = "scopes"
)

func init() {
	validatefn := func(config stow.Config) error {
		_, ok := config.Config(ConfigJSON)
		if !ok {
			return errors.New("missing JSON configuration")
		}

		_, ok = config.Config(ConfigProjectId)
		if !ok {
			return errors.New("missing Project ID")
		}
		return nil
	}
	makefn := func(config stow.Config) (stow.Location, error) {
		_, ok := config.Config(ConfigJSON)
		if !ok {
			return nil, errors.New("missing JSON configuration")
		}

		_, ok = config.Config(ConfigProjectId)
		if !ok {
			return nil, errors.New("missing Project ID")
		}

		// Create a new client
		client, err := newGoogleStorageClient(config)
		if err != nil {
			return nil, err
		}

		// Create a location with given config and client
		loc := &Location{
			config: config,
			client: client,
		}

		return loc, nil
	}

	kindfn := func(u *url.URL) bool {
		return u.Scheme == Kind
	}

	stow.Register(Kind, makefn, kindfn, validatefn)
}

// Attempts to create a session based on the information given.
func newGoogleStorageClient(config stow.Config) (*storage.Service, error) {
	json, _ := config.Config(ConfigJSON)
	var httpClient *http.Client
	scopes := []string{storage.DevstorageReadWriteScope}
	if s, ok := config.Config(ConfigScopes); ok && s != "" {
		scopes = strings.Split(s, ",")
	}
	if json != "" {
		jwtConf, err := google.JWTConfigFromJSON([]byte(json), scopes...)
		if err != nil {
			return nil, err
		}
		httpClient = jwtConf.Client(context.Background())

	} else {
		creds, err := google.FindDefaultCredentials(context.Background(), strings.Join(scopes, ","))
		if err != nil {
			return nil, err
		}
		httpClient = oauth2.NewClient(context.Background(), creds.TokenSource)
	}
	service, err := storage.New(httpClient)
	if err != nil {
		return nil, err
	}

	return service, nil
}
