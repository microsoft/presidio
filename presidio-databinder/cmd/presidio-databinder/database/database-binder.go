package databaseBinder

import (
	"fmt"
	"time"

	// import mssql driver
	_ "github.com/denisenkom/go-mssqldb"
	// import mysql driver
	_ "github.com/go-sql-driver/mysql"
	"github.com/go-xorm/xorm"
	// import postegrsql driver
	_ "github.com/lib/pq"
	// import sqlite driver
	_ "github.com/mattn/go-sqlite3"

	message_types "github.com/presid-io/presidio-genproto/golang"
	log "github.com/presid-io/presidio/pkg/logger"
	"github.com/presid-io/presidio/presidio-databinder/cmd/presidio-databinder/databinder"
)

type dbDataBinder struct {
	driverName       string
	connectionString string
	engine           *xorm.Engine
	tableName        string
}

// New returns new instance of DB Data writter
func New(databinder *message_types.Databinder) databinder.DataBinder {
	// default table name
	tableName := databinder.DbConfig.GetTableName()
	if tableName == "" {
		tableName = "scannerresult"
	}

	db := dbDataBinder{driverName: databinder.GetBindType(), connectionString: databinder.DbConfig.GetConnectionString(), tableName: tableName}
	db.Init()
	return &db
}

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

type anonymizerResult struct {
	ID             int64 `xorm:"id pk not null autoincr"`
	Path           string
	AnonymizedText string    `xorm:"text"`
	Timestamp      time.Time `xorm:"created"`
}

func (databinder *dbDataBinder) getAnonymizerTableName() string {
	return fmt.Sprintf("%sAnonymized", databinder.tableName)
}

func (databinder *dbDataBinder) Init() {
	var err error

	// Connect to DB
	databinder.engine, err = xorm.NewEngine(databinder.driverName, databinder.connectionString)
	if err != nil {
		log.Fatal(err.Error())
	}

	// Create table if not exists
	err = databinder.engine.Table(databinder.tableName).CreateTable(&analyzerResult{})
	if err != nil {
		log.Fatal(err.Error())
	}

	err = databinder.engine.Table(databinder.getAnonymizerTableName()).CreateTable(&anonymizerResult{})
	if err != nil {
		log.Fatal(err.Error())
	}
}

func (databinder *dbDataBinder) WriteAnalyzeResults(results []*message_types.AnalyzeResult, path string) error {
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
	_, err := databinder.engine.Table(databinder.tableName).Insert(&analyzerResultArray)
	if err != nil {
		return err
	}

	log.Info(fmt.Sprintf("path: %s, %d analyzed rows were written to the DB successfully", path, len(results)))
	return nil
}

func (databinder *dbDataBinder) WriteAnonymizeResults(result *message_types.AnonymizeResponse, path string) error {

	r := anonymizerResult{
		AnonymizedText: result.Text,
		Path:           path,
	}

	// Add row to table
	_, err := databinder.engine.Table(databinder.getAnonymizerTableName()).Insert(&r)
	if err != nil {
		log.Error(fmt.Sprintf("error analyzeing %s", path))
		return err
	}

	log.Info(fmt.Sprintf("path: %s, anonymized result was written to the DB successfully, ", path))
	return nil
}
