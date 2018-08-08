package main

import (
	"fmt"

	message_types "github.com/Microsoft/presidio-genproto/golang"
	"github.com/Microsoft/presidio/presidio-datasync/cmd/presidio-datasync/cloudstorage"
	"github.com/Microsoft/presidio/presidio-datasync/cmd/presidio-datasync/database"
	dataSyncInterface "github.com/Microsoft/presidio/presidio-datasync/cmd/presidio-datasync/datasync"
)

func createDataSync(dataSync *message_types.DataSync, dataSyncKind string, resultKind string) (dataSyncInterface.DataSync, error) {
	if isDatabase(dataSyncKind) {
		if dataSync.DbConfig.GetConnectionString() == "" {
			return nil, fmt.Errorf("connectionString var must me set")
		}
		return database.New(dataSync, dataSyncKind, resultKind), nil
	} else if isCloudStorage(dataSyncKind) {
		return cloudStorage.New(dataSync, dataSyncKind), nil
	}

	return nil, fmt.Errorf("unknown dataSync kind")
}

func isDatabase(target string) bool {
	return target == message_types.DataSyncTypesEnum.String(message_types.DataSyncTypesEnum_mssql) ||
		target == message_types.DataSyncTypesEnum.String(message_types.DataSyncTypesEnum_mysql) ||
		target == message_types.DataSyncTypesEnum.String(message_types.DataSyncTypesEnum_oracle) ||
		target == message_types.DataSyncTypesEnum.String(message_types.DataSyncTypesEnum_postgres) ||
		target == message_types.DataSyncTypesEnum.String(message_types.DataSyncTypesEnum_sqlite3)
}

func isCloudStorage(target string) bool {
	return target == message_types.DataSyncTypesEnum.String(message_types.DataSyncTypesEnum_azureblob) ||
		target == message_types.DataSyncTypesEnum.String(message_types.DataSyncTypesEnum_s3) ||
		target == message_types.DataSyncTypesEnum.String(message_types.DataSyncTypesEnum_googlestorage)
}
