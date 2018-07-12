package main

import (
	"time"

	_ "github.com/denisenkom/go-mssqldb"
	_ "github.com/go-sql-driver/mysql"
	"github.com/go-xorm/xorm"

	message_types "github.com/presid-io/presidio-genproto/golang"
	log "github.com/presid-io/presidio/pkg/logger"
)

// Analyze results table scheme
type analyzerResult struct {
	ID            int64 `xorm:"id pk not null autoincr"`
	Field         string
	Propability   float32
	Path          string
	LocationStart int32
	Length        int32
	Timestamp     time.Time `xorm:"created"`
}

var engine *xorm.Engine

func initDatabase() {
	var err error

	// Connect to DB
	engine, err = xorm.NewEngine(driverName, connectionString)
	if err != nil {
		log.Fatal(err.Error())
	}

	// Create table if not exists
	//engine.DropTables(&analyzerResult{})
	err = engine.CreateTables(&analyzerResult{})
	if err != nil {
		log.Fatal(err.Error())
	}

}

func (r *analyzerResult) TableName() string {
	// TODO: CHANGE
	return "users"
}

func writeResultsToDB(results []*message_types.AnalyzeResult, path string) error {
	analyzerResultArray := []analyzerResult{}

	for _, element := range results {
		analyzerResultArray = append(analyzerResultArray, analyzerResult{
			Field:         element.Field.Name,
			Propability:   element.Probability,
			Path:          path,
			LocationStart: element.Location.Start,
			Length:        element.Location.Length,
		})
	}

	// Add rows to table
	_, err := engine.Insert(&analyzerResultArray)
	if err != nil {
		log.Error(err.Error())
		return err
	}

	return nil
}
