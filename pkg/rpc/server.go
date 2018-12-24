package rpc

import (
	"fmt"
	"net"

	"google.golang.org/grpc"

	log "github.com/Microsoft/presidio/pkg/logger"
)

//SetupClient setup grpc listener
func SetupClient(grpcPort int) (net.Listener, *grpc.Server) {

	addr := fmt.Sprintf(":%d", grpcPort)
	log.Info(addr)
	lis, err := net.Listen("tcp", addr)
	if err != nil {
		log.Fatal(err.Error())
	}

	grpcServer := grpc.NewServer()
	return lis, grpcServer

}
