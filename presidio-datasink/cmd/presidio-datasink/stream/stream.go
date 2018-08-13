package stream

import (
	"fmt"
	"path/filepath"

	message_types "github.com/Microsoft/presidio-genproto/golang"
	log "github.com/Microsoft/presidio/pkg/logger"
	"github.com/Microsoft/presidio/pkg/stream"
	"github.com/Microsoft/presidio/pkg/stream/eventhubs"
	"github.com/Microsoft/presidio/pkg/templates"
	"github.com/Microsoft/presidio/presidio-datasink/cmd/presidio-datasink/datasink"
)

type streamDatasink struct {
	stream stream.Stream
}

// New returns new instance of DB Data writter
func New(datasink *message_types.Datasink, kind string) datasink.Datasink {
	var stream stream.Stream
	switch kind {
	case message_types.DatasinkTypesEnum.String(message_types.DatasinkTypesEnum_eventhub):
		stream = eventhubs.New()
		// case message_types.DatasinkTypesEnum.String(message_types.DatasinkTypesEnum_kafka):
		// 	stream = kafka.NewConsumer(datasink.StreamConfig.KafkaConfig.GetAddress(), datasink.StreamConfig.KafkaConfig.GetTopic())
		// case message_types.DatasinkTypesEnum.String(message_types.DatasinkTypesEnum_kinesis):
		// 	stream = kafka.NewConsumer(datasink.StreamConfig.KinesisConfig.GetStreamName, datasink.StreamConfig.KafkaConfig.GetTopic())
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

func addActionToFilePath(path string, action string) string {
	ext := filepath.Ext(path)
	path = path[:len(path)-len(ext)]
	if string(path[0]) == "/" {
		path = path[1:]
	}
	return fmt.Sprintf("%s-%s%s", path, action, ext)
}
