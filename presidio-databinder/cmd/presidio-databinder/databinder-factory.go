package main

import "github.com/presid-io/presidio/presidio-databinder/cmd/presidio-databinder/database"

func createDatabiner(bindType string) {
	if isDatabase(bindType) {
		dbwritter := databaseBinder.New(bindType, connectionString)
		databinderArray = append(databinderArray, &dbwritter)
	}
}
