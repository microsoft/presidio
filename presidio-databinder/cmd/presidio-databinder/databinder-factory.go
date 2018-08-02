package main

import (
	"fmt"

	message_types "github.com/Microsoft/presidio-genproto/golang"
	"github.com/Microsoft/presidio/presidio-databinder/cmd/presidio-databinder/cloudstorage"
	"github.com/Microsoft/presidio/presidio-databinder/cmd/presidio-databinder/database"
)

func createDatabiner(databinder *message_types.Databinder) error {
	if isDatabase(databinder.GetBindType()) {
		if databinder.DbConfig.GetConnectionString() == "" {
			return fmt.Errorf("connectionString var must me set")
		}
		dbwritter := databaseBinder.New(databinder)
		databinderArray = append(databinderArray, &dbwritter)
	} else if isCloudStorage(databinder.GetBindType()) {
		cloudStorageBinder := cloudStorageBinder.New(databinder)
		databinderArray = append(databinderArray, &cloudStorageBinder)
	}

	return nil
}

func isDatabase(target string) bool {
	return target == message_types.DataBinderTypesEnum.String(message_types.DataBinderTypesEnum_mssql) ||
		target == message_types.DataBinderTypesEnum.String(message_types.DataBinderTypesEnum_mysql) ||
		target == message_types.DataBinderTypesEnum.String(message_types.DataBinderTypesEnum_oracle) ||
		target == message_types.DataBinderTypesEnum.String(message_types.DataBinderTypesEnum_oracle) ||
		target == message_types.DataBinderTypesEnum.String(message_types.DataBinderTypesEnum_postgres) ||
		target == message_types.DataBinderTypesEnum.String(message_types.DataBinderTypesEnum_sqlite3)
}

func isCloudStorage(target string) bool {
	return target == message_types.DataBinderTypesEnum.String(message_types.DataBinderTypesEnum_azureblob) ||
		target == message_types.DataBinderTypesEnum.String(message_types.DataBinderTypesEnum_s3) ||
		target == message_types.DataBinderTypesEnum.String(message_types.DataBinderTypesEnum_googlestorage)
}
