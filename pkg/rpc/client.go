package rpc

import (
	"time"

	grpc "google.golang.org/grpc"

	message_types "github.com/presid-io/presidio-genproto/golang"
)

func connect(addr string) (*grpc.ClientConn, error) {

	conn, err := grpc.Dial(addr, grpc.WithInsecure(), grpc.WithTimeout(1*time.Second), grpc.WithBackoffMaxDelay(1*time.Second))
	if err != nil {
		return nil, err
	}
	return conn, nil
}

//SetupAnonymizeService ...
func SetupAnonymizeService(address string) (*message_types.AnonymizeServiceClient, error) {

	conn, err := connect(address)
	if err != nil {
		return nil, err
	}

	client := message_types.NewAnonymizeServiceClient(conn)
	return &client, nil
}

//SetupAnalyzerService ...
func SetupAnalyzerService(address string) (*message_types.AnalyzeServiceClient, error) {
	conn, err := connect(address)
	if err != nil {
		return nil, err
	}
	client := message_types.NewAnalyzeServiceClient(conn)
	return &client, nil
}

//SetupDataBinderService ...
func SetupDataBinderService(address string) (*message_types.DatabinderServiceClient, error) {
	conn, err := connect(address)
	if err != nil {
		return nil, err
	}
	client := message_types.NewDatabinderServiceClient(conn)
	return &client, nil
}
