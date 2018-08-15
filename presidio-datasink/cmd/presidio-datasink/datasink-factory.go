package main

import (
	"fmt"

	message_types "github.com/Microsoft/presidio-genproto/golang"
	"github.com/Microsoft/presidio/presidio-datasink/cmd/presidio-datasink/cloudstorage"
	"github.com/Microsoft/presidio/presidio-datasink/cmd/presidio-datasink/database"
	datasinkInterface "github.com/Microsoft/presidio/presidio-datasink/cmd/presidio-datasink/datasink"
	"github.com/Microsoft/presidio/presidio-datasink/cmd/presidio-datasink/stream"
)

func createDatasink(datasink *message_types.Datasink, resultType string) (datasinkInterface.Datasink, error) {
	if datasink.GetDbConfig() != nil {
		if datasink.DbConfig.GetConnectionString() == "" {
			return nil, fmt.Errorf("connectionString var must me set")
		}
		return database.New(datasink, resultType), nil
	} else if datasink.GetCloudStorageConfig() != nil {
		return cloudStorage.New(datasink), nil
	} else if datasink.GetStreamConfig() != nil {
		return stream.New(datasink), nil
	}

	return nil, fmt.Errorf("unknown datasink kind")
}
