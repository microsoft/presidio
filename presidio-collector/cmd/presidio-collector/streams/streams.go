package streams

import (
	"context"
	"fmt"

	types "github.com/Microsoft/presidio-genproto/golang"

	"github.com/Microsoft/presidio/pkg/stream"
	"github.com/Microsoft/presidio/pkg/stream/eventhubs"
	"github.com/Microsoft/presidio/pkg/stream/kafka"
)

//CreateStream create stream from configuration
func CreateStream(ctx context.Context, streamRequest *types.StreamRequest) stream.Stream {

	config := streamRequest.GetStreamConfig()

	//Kafka
	if config.GetKafkaConfig() != nil {
		c := config.GetKafkaConfig()
		k := kafka.NewConsumer(ctx, c.GetAddress(), c.GetTopic(), fmt.Sprintf("presidio-cg-%s", c.GetTopic()))
		return k
	}

	//Azure Event Hub
	if config.GetEhConfig() != nil {
		c := config.GetEhConfig()
		e := eventhubs.NewConsumer(ctx, c.GetEhConnectionString(), c.GetStorageAccountNameValue(), c.GetStorageAccountKeyValue(), c.GetContainerValue())
		return e
	}

	return nil
}
