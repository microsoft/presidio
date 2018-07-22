package main

import "github.com/presid-io/presidio/presidio-databinder/cmd/presidio-databinder/database"

func createDatabiner(bindType string, connectionString string, tableName string) {
	if isDatabase(bindType) {
		dbwritter := databaseBinder.New(bindType, connectionString, tableName)
		databinderArray = append(databinderArray, &dbwritter)
	}
}
