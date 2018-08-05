package rpc

import (
	"time"

	"context"
	message_types "github.com/Microsoft/presidio-genproto/golang"
	grpc_retry "github.com/grpc-ecosystem/go-grpc-middleware/retry"
	grpc "google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	//"google.golang.org/grpc/resolver"
)

func connect(addr string) (*grpc.ClientConn, error) {

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	callOpts := []grpc_retry.CallOption{
		grpc_retry.WithBackoff(grpc_retry.BackoffLinear(1 * time.Second)),
		grpc_retry.WithCodes(codes.NotFound, codes.Aborted),
	}

	//resolver.SetDefaultScheme("dns")

	conn, err := grpc.DialContext(ctx, addr,
		grpc.WithUnaryInterceptor(grpc_retry.UnaryClientInterceptor(callOpts...)),
		grpc.WithInsecure(),
		grpc.WithBlock(),
		grpc.WithBackoffMaxDelay(5*time.Second),
		grpc.WithBalancerName("round_robin"))

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

//SetupCronJobService ...
func SetupCronJobService(address string) (*message_types.CronJobServiceClient, error) {
	conn, err := connect(address)
	if err != nil {
		return nil, err
	}
	client := message_types.NewCronJobServiceClient(conn)
	return &client, nil
}
