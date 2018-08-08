package database

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

	message_types "github.com/Microsoft/presidio-genproto/golang"
	log "github.com/Microsoft/presidio/pkg/logger"
	"github.com/Microsoft/presidio/presidio-datasync/cmd/presidio-datasync/datasync"
)

type dbDataSync struct {
	driverName       string
	connectionString string
	engine           *xorm.Engine
	tableName        string
	resultKind       string
}

// New returns new instance of DB Data writter
func New(datasync *message_types.DataSync, dataSyncKind string, resultKind string) dataSync.DataSync {
	// default table name
	tableName := datasync.DbConfig.GetTableName()
	if tableName == "" {
		tableName = "scannerresult"
	}

	db := dbDataSync{driverName: dataSyncKind, connectionString: datasync.DbConfig.GetConnectionString(), tableName: tableName, resultKind: resultKind}
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

func (datasync *dbDataSync) Init() {
	var err error

	// Connect to DB
	datasync.engine, err = xorm.NewEngine(datasync.driverName, datasync.connectionString)
	if err != nil {
		log.Fatal(err.Error())
	}

	// Create table if not exists
	if datasync.resultKind == "analyze" {
		err = datasync.engine.Table(datasync.tableName).CreateTable(&analyzerResult{})
		if err != nil {
			log.Fatal(err.Error())
		}
	} else if datasync.resultKind == "anonymize" {
		err = datasync.engine.Table(datasync.tableName).CreateTable(&anonymizerResult{})
		if err != nil {
			log.Fatal(err.Error())
		}
	}
}

func (datasync *dbDataSync) WriteAnalyzeResults(results []*message_types.AnalyzeResult, path string) error {
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
	_, err := datasync.engine.Table(datasync.tableName).Insert(&analyzerResultArray)
	if err != nil {
		return err
	}

	log.Info(fmt.Sprintf("path: %s, %d analyzed rows were written to the DB successfully", path, len(results)))
	return nil
}

func (datasync *dbDataSync) WriteAnonymizeResults(result *message_types.AnonymizeResponse, path string) error {
	r := anonymizerResult{
		AnonymizedText: result.Text,
		Path:           path,
	}

	// Add row to table
	_, err := datasync.engine.Table(datasync.tableName).Insert(&r)
	if err != nil {
		log.Error(fmt.Sprintf("error analyzeing %s", path))
		return err
	}

	log.Info(fmt.Sprintf("path: %s, anonymized result was written to the DB successfully, ", path))
	return nil
}
