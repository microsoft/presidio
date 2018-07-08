package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"time"

	_ "github.com/denisenkom/go-mssqldb"
	"github.com/go-xorm/xorm"
	"github.com/joho/godotenv"
	"google.golang.org/grpc/reflection"

	message_types "github.com/presidium-io/presidium-genproto/golang"
	"github.com/presidium-io/presidium/pkg/rpc"
)

type analyzerResultTable struct {
	ID          int64 `xorm:"id pk not null autoincr"`
	Field       string
	Propability float32
	Path        string
	Timestamp   time.Time `xorm:"created"`
}

var (
	grpcPort         = os.Getenv("GRPC_PORT")
	driverName       string
	connectionString string
	engine           *xorm.Engine
)

type server struct{}

func main() {
	// Setup server
	lis, s := rpc.SetupClient(grpcPort)

	message_types.RegisterDatabinderServiceServer(s, &server{})
	reflection.Register(s)

	var err error

	// Connect to DB
	engine, err = xorm.NewEngine(driverName, connectionString)
	if err != nil {
		log.Fatal(err)
	}

	// Create table if not exists
	//engine.DropTables(&analyzerResult{})
	err = engine.CreateTables(&analyzerResultTable{})
	if err != nil {
		log.Fatal(err)
	}

	// Listen for client requests
	if err := s.Serve(lis); err != nil {
		log.Fatal(err.Error())
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

	if grpcPort == "" {
		// Set to default
		grpcPort = "5000"
	}
}

func (s *server) Apply(ctx context.Context, r *message_types.DatabinderRequest) (*message_types.DatabinderResponse, error) {
	err := writeResultsToDB(r.AnalyzeResults, r.Path)
	return &message_types.DatabinderResponse{StatusCode: 200}, err
}

func writeResultsToDB(results []*message_types.AnalyzeResult, path string) error {
	analyzerResultArray := []analyzerResultTable{}

	for _, element := range results {
		analyzerResultArray = append(analyzerResultArray, analyzerResultTable{
			Field:       element.Field.Name,
			Propability: element.Probability,
			Path:        path,
		})
	}

	// Add rows to table
	_, err := engine.Insert(&analyzerResultArray)
	if err != nil {
		fmt.Println(err)
		return err
	}
	return nil
}
