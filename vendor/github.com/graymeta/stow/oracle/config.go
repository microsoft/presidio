package swift

import (
	"errors"
	"fmt"
	"net/http"
	"net/url"
	"strings"

	"github.com/graymeta/stow"
	"github.com/ncw/swift"
)

const (
	// ConfigUsername is the username associated with the account
	ConfigUsername = "username"

	// ConfigPassword is the user password associated with the account
	ConfigPassword = "password"

	// ConfigAuthEndpoint is the identity domain associated with the account
	ConfigAuthEndpoint = "authorization_endpoint"
)

// Kind is the kind of Location this package provides.
const Kind = "oracle"

func init() {
	validatefn := func(config stow.Config) error {
		_, ok := config.Config(ConfigUsername)
		if !ok {
			return errors.New("missing account username")
		}

		_, ok = config.Config(ConfigPassword)
		if !ok {
			return errors.New("missing account password")
		}

		_, ok = config.Config(ConfigAuthEndpoint)
		if !ok {
			return errors.New("missing authorization endpoint")
		}
		return nil
	}
	makefn := func(config stow.Config) (stow.Location, error) {
		_, ok := config.Config(ConfigUsername)
		if !ok {
			return nil, errors.New("missing account username")
		}

		_, ok = config.Config(ConfigPassword)
		if !ok {
			return nil, errors.New("missing account password")
		}

		_, ok = config.Config(ConfigAuthEndpoint)
		if !ok {
			return nil, errors.New("missing authorization endpoint")
		}

		l := &location{
			config: config,
		}

		var err error
		l.client, err = newSwiftClient(l.config)
		if err != nil {
			return nil, err
		}

		return l, nil
	}

	kindfn := func(u *url.URL) bool {
		return u.Scheme == Kind
	}

	stow.Register(Kind, makefn, kindfn, validatefn)
}

func newSwiftClient(cfg stow.Config) (*swift.Connection, error) {
	client, err := parseConfig(cfg)
	if err != nil {
		return nil, err
	}

	err = client.Authenticate()
	if err != nil {
		return nil, errors.New("unable to authenticate")
	}
	return client, nil
}

func parseConfig(cfg stow.Config) (*swift.Connection, error) {
	cfgUsername, _ := cfg.Config(ConfigUsername)
	cfgAuthEndpoint, _ := cfg.Config(ConfigAuthEndpoint)

	// Auth Endpoint contains most of the information needed to make a client,
	// find the indexes of the symbols that separate them.
	dotIndex := strings.Index(cfgAuthEndpoint, `.`)
	if dotIndex == -1 {
		return nil, errors.New("stow: oracle: bad format for " + ConfigAuthEndpoint)
	}
	dashIndex := strings.Index(cfgAuthEndpoint[:dotIndex], `-`)
	slashIndex := strings.Index(cfgAuthEndpoint, `//`) + 1 // Add 1 to move index to second slash

	var metered bool

	// metered storage endpoints should not have a dash before the dot index.
	if dashIndex == -1 {
		metered = true
	}

	var swiftTenantName, swiftUsername, instanceName string
	var startIndex int

	if metered {
		startIndex = slashIndex + 1
		instanceName = "Storage"
	} else {
		startIndex = dashIndex + 1
		instanceName = cfgAuthEndpoint[slashIndex+1 : dashIndex]
	}

	swiftTenantName = cfgAuthEndpoint[startIndex:dotIndex]
	swiftUsername = fmt.Sprintf("%s-%s:%s", instanceName, swiftTenantName, cfgUsername)

	// The client's key is the user account's Password
	swiftKey, _ := cfg.Config(ConfigPassword)

	client := swift.Connection{
		UserName:  swiftUsername,
		ApiKey:    swiftKey,
		AuthUrl:   cfgAuthEndpoint,
		Tenant:    swiftTenantName,
		Transport: &fixLastModifiedTransport{http.DefaultTransport},
	}

	return &client, nil
}

type fixLastModifiedTransport struct {
	http.RoundTripper
}

func (t *fixLastModifiedTransport) RoundTrip(r *http.Request) (*http.Response, error) {
	res, err := t.RoundTripper.RoundTrip(r)
	if err != nil {
		return res, err
	}
	if lastMod := res.Header.Get("Last-Modified"); strings.Contains(lastMod, "UTC") {
		res.Header.Set("Last-Modified", strings.Replace(lastMod, "UTC", "GMT", 1))
	}
	return res, err
}
