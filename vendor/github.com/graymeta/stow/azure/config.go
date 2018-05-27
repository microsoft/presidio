package azure

import (
	"errors"
	"net/url"

	az "github.com/Azure/azure-sdk-for-go/storage"
	"github.com/graymeta/stow"
)

// ConfigAccount and ConfigKey are the supported configuration items for
// Azure blob storage.
const (
	ConfigAccount = "account"
	ConfigKey     = "key"
)

// Kind is the kind of Location this package provides.
const Kind = "azure"

func init() {
	validatefn := func(config stow.Config) error {
		_, ok := config.Config(ConfigAccount)
		if !ok {
			return errors.New("missing account id")
		}
		_, ok = config.Config(ConfigKey)
		if !ok {
			return errors.New("missing auth key")
		}
		return nil
	}
	makefn := func(config stow.Config) (stow.Location, error) {
		_, ok := config.Config(ConfigAccount)
		if !ok {
			return nil, errors.New("missing account id")
		}
		_, ok = config.Config(ConfigKey)
		if !ok {
			return nil, errors.New("missing auth key")
		}
		l := &location{
			config: config,
		}
		var err error
		l.client, err = newBlobStorageClient(l.config)
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

func newBlobStorageClient(cfg stow.Config) (*az.BlobStorageClient, error) {
	acc, ok := cfg.Config(ConfigAccount)
	if !ok {
		return nil, errors.New("missing account id")
	}
	key, ok := cfg.Config(ConfigKey)
	if !ok {
		return nil, errors.New("missing auth key")
	}
	basicClient, err := az.NewBasicClient(acc, key)
	if err != nil {
		return nil, errors.New("bad credentials")
	}
	client := basicClient.GetBlobService()
	return &client, err
}
