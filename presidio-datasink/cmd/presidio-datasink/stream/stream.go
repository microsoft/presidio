package stream

import (
	"context"
	"fmt"

	types "github.com/Microsoft/presidio-genproto/golang"

	log "github.com/Microsoft/presidio/pkg/logger"
	"github.com/Microsoft/presidio/pkg/presidio"
	"github.com/Microsoft/presidio/pkg/stream"
	"github.com/Microsoft/presidio/pkg/stream/eventhubs"
	"github.com/Microsoft/presidio/pkg/stream/kafka"
	"github.com/Microsoft/presidio/presidio-datasink/cmd/presidio-datasink/datasink"
)

type streamDatasink struct {
	stream stream.Stream
}

// New returns new instance of stream Data writer
func New(datasink *types.Datasink) datasink.Datasink {
	var stream stream.Stream

	if datasink.StreamConfig.GetEhConfig() != nil {
		stream = eventhubs.NewProducer(context.Background(), datasink.StreamConfig.GetEhConfig().GetEhConnectionString())
	} else if datasink.StreamConfig.GetKafkaConfig() != nil {
		c := datasink.StreamConfig.GetKafkaConfig()
		stream = kafka.NewProducer(c.GetAddress(), c.GetTopic())
	}

	streamDatasink := streamDatasink{stream: stream}
	return &streamDatasink
}

func (datasink *streamDatasink) Init() {
}

func (datasink *streamDatasink) WriteAnalyzeResults(results []*types.AnalyzeResult, path string) error {
	resultString, err := presidio.ConvertInterfaceToJSON(&types.DatasinkRequest{
		AnalyzeResults: results,
		Path:           path,
	})
	if err != nil {
		log.Error(err.Error())
		return err
	}

	datasink.stream.Send(resultString)
	if err != nil {
		return err
	}

	log.Info(fmt.Sprintf("%d rows were written to the stream successfully", len(results)))
	return nil
}

func (datasink *streamDatasink) WriteAnonymizeResults(result *types.AnonymizeResponse, path string) error {
	resultString, err := presidio.ConvertInterfaceToJSON(&types.DatasinkRequest{
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
