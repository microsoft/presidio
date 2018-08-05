package rpc

import (
	"fmt"
	"net"

	log "github.com/Microsoft/presidio/pkg/logger"
	"google.golang.org/grpc"
)

//SetupClient setup grpc listener
func SetupClient(grpcPort string) (net.Listener, *grpc.Server) {

	addr := fmt.Sprintf(":%s", grpcPort)
	log.Info(addr)
	lis, err := net.Listen("tcp", addr)
	if err != nil {
		log.Fatal(err.Error())
	}

	grpcServer := grpc.NewServer()
	return lis, grpcServer

}
