package main

import (
	"fmt"

	message_types "github.com/Microsoft/presidio-genproto/golang"
	"github.com/Microsoft/presidio/presidio-datasink/cmd/presidio-datasink/cloudstorage"
	"github.com/Microsoft/presidio/presidio-datasink/cmd/presidio-datasink/database"
	datasinkInterface "github.com/Microsoft/presidio/presidio-datasink/cmd/presidio-datasink/datasink"
)

func createDatasink(datasink *message_types.Datasink, datasinkKind string, resultKind string) (datasinkInterface.Datasink, error) {
	if isDatabase(datasinkKind) {
		if datasink.DbConfig.GetConnectionString() == "" {
			return nil, fmt.Errorf("connectionString var must me set")
		}
		return database.New(datasink, datasinkKind, resultKind), nil
	} else if isCloudStorage(datasinkKind) {
		return cloudStorage.New(datasink, datasinkKind), nil
	}

	return nil, fmt.Errorf("unknown datasink kind")
}

func isDatabase(target string) bool {
	return target == message_types.DatasinkTypesEnum.String(message_types.DatasinkTypesEnum_mssql) ||
		target == message_types.DatasinkTypesEnum.String(message_types.DatasinkTypesEnum_mysql) ||
		target == message_types.DatasinkTypesEnum.String(message_types.DatasinkTypesEnum_oracle) ||
		target == message_types.DatasinkTypesEnum.String(message_types.DatasinkTypesEnum_postgres) ||
		target == message_types.DatasinkTypesEnum.String(message_types.DatasinkTypesEnum_sqlite3)
}

func isCloudStorage(target string) bool {
	return target == message_types.DatasinkTypesEnum.String(message_types.DatasinkTypesEnum_azureblob) ||
		target == message_types.DatasinkTypesEnum.String(message_types.DatasinkTypesEnum_s3) ||
		target == message_types.DatasinkTypesEnum.String(message_types.DatasinkTypesEnum_googlestorage)
}
