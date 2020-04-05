package database

import (
	"time"

	// import mssql driver
	_ "github.com/denisenkom/go-mssqldb"
	// import mysql driver
	_ "github.com/go-sql-driver/mysql"
	"github.com/go-xorm/xorm"
	// import postgresql driver
	_ "github.com/lib/pq"

	types "github.com/Microsoft/presidio-genproto/golang"

	log "github.com/Microsoft/presidio/pkg/logger"
	"github.com/Microsoft/presidio/presidio-datasink/cmd/presidio-datasink/datasink"
)

type dbDatasink struct {
	driverName       string
	connectionString string
	engine           *xorm.Engine
	tableName        string
	resultType       string
}

// New returns new instance of DB Data writer
func New(datasink *types.Datasink, resultType string) datasink.Datasink {
	// default table name
	tableName := datasink.DbConfig.GetTableName()
	if tableName == "" {
		tableName = "scannerresult"
	}

	db := dbDatasink{driverName: datasink.GetDbConfig().GetType(), connectionString: datasink.GetDbConfig().GetConnectionString(),
		tableName: tableName, resultType: resultType}
	db.Init()
	return &db
}

// Analyze results table scheme
type analyzerResult struct {
	ID            int64 `xorm:"id pk not null autoincr"`
	Field         string
	Score         float32
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

func (datasink *dbDatasink) Init() {
	var err error

	// Connect to DB
	datasink.engine, err = xorm.NewEngine(datasink.driverName, datasink.connectionString)
	if err != nil {
		log.Fatal(err.Error())
	}

	// Create table if not exists
	if datasink.resultType == "analyze" {
		err = datasink.engine.Table(datasink.tableName).CreateTable(&analyzerResult{})
		if err != nil {
			log.Fatal(err.Error())
		}
	} else if datasink.resultType == "anonymize" {
		err = datasink.engine.Table(datasink.tableName).CreateTable(&anonymizerResult{})
		if err != nil {
			log.Fatal(err.Error())
		}
	}
}

func (datasink *dbDatasink) WriteAnalyzeResults(results []*types.AnalyzeResult, path string) error {
	analyzerResultArray := []analyzerResult{}

	for _, element := range results {
		analyzerResultArray = append(analyzerResultArray, analyzerResult{
			Field:         element.Field.Name,
			Score:         element.Score,
			Path:          path,
			LocationStart: element.Location.Start,
			Length:        element.Location.Length,
		})
	}

	// Add rows to table
	_, err := datasink.engine.Table(datasink.tableName).Insert(&analyzerResultArray)
	if err != nil {
		return err
	}

	log.Info("path: %s, %d analyzed rows were written to the DB successfully", path, len(results))
	return nil
}

func (datasink *dbDatasink) WriteAnonymizeResults(result *types.AnonymizeResponse, path string) error {
	r := anonymizerResult{
		AnonymizedText: result.Text,
		Path:           path,
	}

	// Add row to table
	_, err := datasink.engine.Table(datasink.tableName).Insert(&r)
	if err != nil {
		return err
	}

	log.Info("path: %s, anonymized result was written to the DB successfully, ", path)
	return nil
}
