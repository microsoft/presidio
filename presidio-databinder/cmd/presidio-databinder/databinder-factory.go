package main

import (
	"fmt"

	message_types "github.com/Microsoft/presidio-genproto/golang"
	"github.com/Microsoft/presidio/presidio-databinder/cmd/presidio-databinder/database"
)

func createDatabiner(databinder *message_types.Databinder) error {
	if isDatabase(databinder.GetBindType()) {
		if databinder.DbConfig.GetConnectionString() == "" {
			return fmt.Errorf("connectionString var must me set")
		}
		dbwritter := databaseBinder.New(databinder.GetBindType(), databinder.DbConfig.GetConnectionString(), databinder.DbConfig.GetTableName())
		databinderArray = append(databinderArray, &dbwritter)
	}

	return nil
}
