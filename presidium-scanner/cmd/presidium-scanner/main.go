package main

import (
	"flag"
	"fmt"

	//	"github.com/presidium-io/presidium/pkg/kv"
	//"github.com/presidium-io/presidium/pkg/kv/consul"

	"github.com/presidium-io/presidium/pkg/logger"
	_ "github.com/presidium-io/presidium/pkg/storage"
)

func main() {
	projectID := flag.String("project", "", "project id")
	flag.Parse()
	logger.Info(fmt.Sprintf("Scanning project %s", *projectID))

	// _, err := consul.GetKVPair(*projectID)
	// if err != nil {
	// 	logger.Fatal(fmt.Sprintf("Project not found %s", *projectID))
	// }

}
