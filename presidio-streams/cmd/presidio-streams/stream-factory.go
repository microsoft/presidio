package main

import (
	"context"

	"os"

	"github.com/Microsoft/presidio/pkg/stream"
	"github.com/Microsoft/presidio/pkg/stream/eventhubs"
	"github.com/Microsoft/presidio/pkg/stream/kafka"
	"github.com/Microsoft/presidio/pkg/stream/kinesis"
)

func createStream() stream.Stream {
	config := streamRequest.GetStreamConfig()
	ctx := context.Background()
	if streamRequest.GetKind() == "kafka" && config.KafkaConfig != nil {
		c := config.GetKafkaConfig()
		k := kafka.NewConsumer(ctx, c.GetAddress(), c.GetTopic())
		return k
	}

	if streamRequest.GetKind() == "eventhub" && config.EhConfig != nil {
		c := config.GetEhConfig()
		//TODO: This will deprecated in favor of EPH
		e := eventhubs.NewConsumer(ctx, c.GetEhConnectionString(), os.Getenv("PARTITION_ID"))
		return e
	}
	if streamRequest.GetKind() == "kinesis" && config.EhConfig != nil {
		c := config.GetKinesisConfig()
		k := kinesis.NewConsumer(ctx, c.EndpointAddress, c.AwsSecretAccessKey, c.AwsRegion, c.AwsAccessKeyId, c.RedisUrl, c.GetStreamName())
		return k
	}
	return nil
}
