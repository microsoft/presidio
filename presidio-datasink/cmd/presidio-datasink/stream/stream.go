package stream

import (
	"context"
	"fmt"
	"os"

	message_types "github.com/Microsoft/presidio-genproto/golang"
	log "github.com/Microsoft/presidio/pkg/logger"
	"github.com/Microsoft/presidio/pkg/stream"
	"github.com/Microsoft/presidio/pkg/stream/eventhubs"
	"github.com/Microsoft/presidio/pkg/stream/kafka"
	"github.com/Microsoft/presidio/pkg/stream/kinesis"
	"github.com/Microsoft/presidio/pkg/templates"
	"github.com/Microsoft/presidio/presidio-datasink/cmd/presidio-datasink/datasink"
)

type streamDatasink struct {
	stream stream.Stream
}

// New returns new instance of DB Data writer
func New(datasink *message_types.Datasink, kind string) datasink.Datasink {
	var stream stream.Stream
	var ctx = context.Background()
	switch kind {
	case message_types.DatasinkTypesEnum.String(message_types.DatasinkTypesEnum_eventhub):
		c := datasink.StreamConfig.GetEhConfig()
		//TODO: This will deprecated in favor of EPH
		stream = eventhubs.NewConsumer(ctx, c.GetEhConnectionString(), os.Getenv("PARTITION_ID"))
	case message_types.DatasinkTypesEnum.String(message_types.DatasinkTypesEnum_kafka):
		c := datasink.StreamConfig.GetKafkaConfig()
		stream = kafka.NewConsumer(ctx, c.GetAddress(), c.GetTopic())
	case message_types.DatasinkTypesEnum.String(message_types.DatasinkTypesEnum_kinesis):
		c := datasink.StreamConfig.GetKinesisConfig()
		stream = kinesis.NewConsumer(ctx, c.EndpointAddress, c.AwsSecretAccessKey, c.AwsRegion, c.AwsAccessKeyId, c.RedisUrl, c.GetStreamName())
	}

	streamDatasink := streamDatasink{stream: stream}
	return &streamDatasink
}

func (datasink *streamDatasink) Init() {
}

func (datasink *streamDatasink) WriteAnalyzeResults(results []*message_types.AnalyzeResult, path string) error {
	resultString, err := templates.ConvertInterfaceToJSON(&message_types.DatasinkRequest{
		AnalyzeResults: results,
		Path:           path,
	})
	if err != nil {
		log.Error(err.Error())
		return err
	}

	err = datasink.stream.Send(resultString)
	if err != nil {
		log.Error(err.Error())
		return err
	}

	log.Info(fmt.Sprintf("%d rows were written to the stream successfully", len(results)))
	return nil
}

func (datasink *streamDatasink) WriteAnonymizeResults(result *message_types.AnonymizeResponse, path string) error {
	resultString, err := templates.ConvertInterfaceToJSON(&message_types.DatasinkRequest{
		AnonymizeResult: result,
		Path:            path,
	})

	if err != nil {
		log.Error(err.Error())
		return err
	}

	err = datasink.stream.Send(resultString)
	if err != nil {
		log.Error(err.Error())
		return err
	}

	log.Info("Analyzed result was written to the stream successfully")
	return nil
}
