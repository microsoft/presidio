package main

import (
	"fmt"
	"log"
	"os"
	"strconv"
	"time"

	_ "github.com/denisenkom/go-mssqldb"
	"github.com/gin-gonic/gin"
	"github.com/go-xorm/xorm"
	"github.com/joho/godotenv"
	"github.com/presidium-io/presidium/pkg/server"
)

type analyzerResult struct {
	Field        string
	Propability  float64
	FileName     string
	ConainerName string
	Timestamp    time.Time `xorm:"created"`
}

var (
	webPort          = os.Getenv("WEB_PORT")
	driverName       string
	connectionString string
)

func main() {
	// Setup server
	port, err := strconv.Atoi(webPort)
	if err != nil {
		log.Fatal(err.Error())
	}

	r := server.Setup(port)
	server.Start(r)

	v1 := r.Group("/api/v1")
	{
		v1.POST("analyzeResult", writeAnalyzeResults)
	}
	// Get input from sidecar

	// Connect to DB
	engine, err := xorm.NewEngine(driverName, connectionString)
	if err != nil {
		fmt.Println(err)
		return
	}

	engine.ShowSQL(true)

	// Create table if not exists
	err = engine.CreateTables(&analyzerResult{})
	if err != nil {
		fmt.Println(err)
		return
	}

	row := analyzerResult{
		Field:        "PHONE_NUMBER",
		Propability:  1.0,
		FileName:     "test.txt",
		ConainerName: "containername",
	}

	// Add rows to table
	_, err = engine.Insert(row)
	if err != nil {
		fmt.Println(err)
		return
	}

}

func init() {
	err := godotenv.Load()
	if err != nil {
		log.Fatal("Error loading .env file")
	}

	driverName = os.Getenv("DRIVER_NAME")
	connectionString = os.Getenv("DB_CONNECTION_STRING")

	if driverName == "" {
		log.Fatal("DRIVER_NAME env var must me set")
	}

	if connectionString == "" {
		log.Fatal("DB_CONNECTION_STRING env var must me set")
	}
}

func writeAnalyzeResults(c *gin.Context) {

}
