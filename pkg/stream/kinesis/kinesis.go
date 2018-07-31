package kinesis

import (
	"context"
	"fmt"
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

//NewProducer for kinesis stream
func NewProducer(address string, streamName string) stream.Stream {
	p := kin.New(session.New(), &aws.Config{})

	return &kinesis{
		producer:   p,
		streamName: streamName,
	}
}

//NewConsumer for kinesis stream
func NewConsumer(address string, streamName string) stream.Stream {

	// redis checkpoint
	ck, err := checkpoint.New("presidio")
	if err != nil {
		log.Fatal(fmt.Sprintf("checkpoint error: %v", err))
	}

	// consumer
	c, err := consumer.New(streamName, consumer.WithCheckpoint(ck))
	if err != nil {
		log.Fatal(fmt.Sprintf("consumer error: %v", err))
	}

	// use cancel func to signal shutdown
	ctx, cancel := context.WithCancel(context.Background())

	// trap SIGINT, wait to trigger shutdown
	signals := make(chan os.Signal, 1)
	signal.Notify(signals, os.Interrupt)

	go func() {
		<-signals
		cancel()
	}()

	return &kinesis{
		consumer: c,
		ctx:      ctx,
	}

}

//Receive message from kinesis stream
func (k *kinesis) Receive(receiveFunc stream.ReceiveFunc) error {

	// scan stream
	err := k.consumer.Scan(k.ctx, func(r *consumer.Record) consumer.ScanStatus {

		receiveFunc(string(r.Data))

		// continue scanning
		return consumer.ScanStatus{}
	})
	if err != nil {
		log.Fatal(fmt.Sprintf("scan error: %v", err))
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
		log.Error(fmt.Sprintf("error putting records: %v", err))
	}
	return nil
}
