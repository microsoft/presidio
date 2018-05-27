package swift

import (
	"errors"
	"net/http"
	"net/url"

	"github.com/graymeta/stow"
	"github.com/ncw/swift"
)

// Config key constants.
const (
	ConfigUsername      = "username"
	ConfigKey           = "key"
	ConfigTenantName    = "tenant_name"
	ConfigTenantAuthURL = "tenant_auth_url"
)

// Kind is the kind of Location this package provides.
const Kind = "swift"

func init() {
	validatefn := func(config stow.Config) error {
		_, ok := config.Config(ConfigUsername)
		if !ok {
			return errors.New("missing account username")
		}
		_, ok = config.Config(ConfigKey)
		if !ok {
			return errors.New("missing api key")
		}
		_, ok = config.Config(ConfigTenantName)
		if !ok {
			return errors.New("missing tenant name")
		}
		_, ok = config.Config(ConfigTenantAuthURL)
		if !ok {
			return errors.New("missing tenant auth url")
		}
		return nil
	}
	makefn := func(config stow.Config) (stow.Location, error) {
		_, ok := config.Config(ConfigUsername)
		if !ok {
			return nil, errors.New("missing account username")
		}
		_, ok = config.Config(ConfigKey)
		if !ok {
			return nil, errors.New("missing api key")
		}
		_, ok = config.Config(ConfigTenantName)
		if !ok {
			return nil, errors.New("missing tenant name")
		}
		_, ok = config.Config(ConfigTenantAuthURL)
		if !ok {
			return nil, errors.New("missing tenant auth url")
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
	username, _ := cfg.Config(ConfigUsername)
	key, _ := cfg.Config(ConfigKey)
	tenantName, _ := cfg.Config(ConfigTenantName)
	tenantAuthURL, _ := cfg.Config(ConfigTenantAuthURL)
	client := swift.Connection{
		UserName: username,
		ApiKey:   key,
		AuthUrl:  tenantAuthURL,
		//Domain:   "domain", // Name of the domain (v3 auth only)
		Tenant: tenantName, // Name of the tenant (v2 auth only)
		// Add Default transport
		Transport: http.DefaultTransport,
	}
	err := client.Authenticate()
	if err != nil {
		return nil, errors.New("Unable to authenticate")
	}
	return &client, nil
}
