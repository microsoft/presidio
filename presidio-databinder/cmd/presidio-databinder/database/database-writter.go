package databaseBinder

import (
	"time"

	_ "github.com/denisenkom/go-mssqldb"
	_ "github.com/go-sql-driver/mysql"
	"github.com/go-xorm/xorm"
	message_types "github.com/presid-io/presidio-genproto/golang"
	log "github.com/presid-io/presidio/pkg/logger"
	"github.com/presid-io/presidio/pkg/modules/databinder"
)

type dBDataBinder struct {
	driverName       string
	connectionString string
	engine           *xorm.Engine
}

// New returns new instance of DB Data writter
func New(driverName string, connectionString string) databinder.DataBinder {
	db := dBDataBinder{driverName: driverName, connectionString: connectionString}
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

func (databinder *dBDataBinder) Init() {
	var err error

	// Connect to DB
	databinder.engine, err = xorm.NewEngine(databinder.driverName, databinder.connectionString)
	if err != nil {
		log.Fatal(err.Error())
	}

	// Create table if not exists
	err = databinder.engine.CreateTables(&analyzerResult{})
	if err != nil {
		log.Fatal(err.Error())
	}
}

func (r *analyzerResult) TableName() string {
	// TODO: CHANGE NAME
	return "analyzerresults"
}

func (databinder *dBDataBinder) WriteResults(results []*message_types.AnalyzeResult, path string) error {
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
	_, err := databinder.engine.Insert(&analyzerResultArray)
	if err != nil {
		log.Error(err.Error())
		return err
	}

	return nil
}
