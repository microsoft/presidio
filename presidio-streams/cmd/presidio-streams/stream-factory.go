package main

import (
	"context"

	"github.com/Microsoft/presidio/pkg/stream"
	"github.com/Microsoft/presidio/pkg/stream/eventhubs"
	"github.com/Microsoft/presidio/pkg/stream/kafka"
	"github.com/Microsoft/presidio/pkg/stream/kinesis"
)

func createStream() stream.Stream {
	config := streamRequest.GetStreamConfig()
	ctx := context.Background()

	//Kafka
	if config.GetKafkaConfig() != nil {
		c := config.GetKafkaConfig()
		k := kafka.NewConsumer(ctx, c.GetAddress(), c.GetTopic())
		return k
	}

	//Azure Event Hub
	if config.GetEhConfig() != nil {
		c := config.GetEhConfig()

		e := eventhubs.NewConsumer(ctx, c.GetEhConnectionString(), "", "", "")
		return e
	}

	//Kinesis
	if config.GetKinesisConfig() != nil {
		c := config.GetKinesisConfig()
		k := kinesis.NewConsumer(ctx, c.EndpointAddress, c.AwsSecretAccessKey, c.AwsRegion, c.AwsAccessKeyId, c.RedisUrl, c.GetStreamName())
		return k
	}
	return nil
}
