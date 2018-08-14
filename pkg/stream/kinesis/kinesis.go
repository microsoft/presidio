package kinesis

import (
	"context"
	"os"
	"os/signal"
	"time"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	kin "github.com/aws/aws-sdk-go/service/kinesis"
	consumer "github.com/harlow/kinesis-consumer"
	checkpoint "github.com/harlow/kinesis-consumer/checkpoint/redis"

	log "github.com/Microsoft/presidio/pkg/logger"
	"github.com/Microsoft/presidio/pkg/stream"
)

type kinesis struct {
	consumer   *consumer.Consumer
	producer   *kin.Kinesis
	ctx        context.Context
	streamName string
}

// Required env vars
//  AWS_ACCESS_KEY=
//  AWS_REGION=
//  AWS_SECRET_KEY=
//  REDIS_URL=

func verifyEnvVars(accessKey string, region string, secretKey string, redisUrl string) {
	os.Setenv("AWS_ACCESS_KEY", accessKey)
	os.Setenv("AWS_REGION", region)
	os.Setenv("AWS_SECRET_KEY", secretKey)
	os.Setenv("REDIS_URL", redisUrl)
}

//NewProducer for kinesis stream
func NewProducer(accessKey string, endpoint string, region string, secretKey string, redisUrl string, streamName string) stream.Stream {
	verifyEnvVars(accessKey, region, secretKey, redisUrl)

	config := aws.NewConfig()
	config = config.WithEndpoint(endpoint)
	s, err := session.NewSession(config)
	if err != nil {
		log.Fatal("session error: %v", err)
	}
	p := kin.New(s, config)

	return &kinesis{
		producer:   p,
		streamName: streamName,
	}
}

//NewConsumer for kinesis stream
func NewConsumer(ctx context.Context, endpoint string, accessKey string, region string, secretKey string, redisUrl string, streamName string) stream.Stream {

	verifyEnvVars(accessKey, region, secretKey, redisUrl)

	// redis checkpoint
	ck, err := checkpoint.New(streamName)
	if err != nil {
		log.Fatal("checkpoint error: %v", err)
	}

	// consumer
	config := aws.NewConfig()
	config = config.WithEndpoint(endpoint)

	s, err := session.NewSession(config)
	if err != nil {
		log.Fatal("session error: %v", err)
	}
	client := kin.New(s)
	c, err := consumer.New(streamName, consumer.WithClient(client), consumer.WithCheckpoint(ck))
	if err != nil {
		log.Fatal("consumer error: %v", err)
	}

	// use cancel func to signal shutdown
	cancelCtx, cancel := context.WithCancel(ctx)

	// trap SIGINT, wait to trigger shutdown
	signals := make(chan os.Signal, 1)
	signal.Notify(signals, os.Interrupt)

	go func() {
		<-signals
		cancel()
	}()

	return &kinesis{
		consumer: c,
		ctx:      cancelCtx,
	}

}

//Receive message from kinesis stream
func (k *kinesis) Receive(receiveFunc stream.ReceiveFunc) error {

	// scan stream
	err := k.consumer.Scan(k.ctx, func(r *consumer.Record) consumer.ScanStatus {

		receiveFunc(aws.StringValue(r.PartitionKey), aws.StringValue(r.SequenceNumber), string(r.Data))

		// continue scanning
		return consumer.ScanStatus{}
	})
	if err != nil {
		log.Fatal("scan error: %v", err)
	}

	return nil
}

//TODO: Convert to batch send
//Send message to kinesis stream
func (k *kinesis) Send(message string) error {

	var records []*kin.PutRecordsRequestEntry
	records = append(records, &kin.PutRecordsRequestEntry{
		Data:         []byte(message),
		PartitionKey: aws.String(time.Now().Format(time.RFC3339Nano)),
	})

	_, err := k.producer.PutRecords(&kin.PutRecordsInput{
		StreamName: aws.String(k.streamName),
		Records:    records,
	})
	if err != nil {
		log.Error("error putting records: %v", err)
	}
	return nil
}
