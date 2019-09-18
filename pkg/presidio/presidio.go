package presidio

import (
	"context"
	"encoding/json"
	"fmt"

	types "github.com/Microsoft/presidio-genproto/golang"
	"github.com/Microsoft/presidio/pkg/cache"
)

//ServicesAPI interface for services action
type ServicesAPI interface {
	SetupAnalyzerService()
	SetupAnonymizerService()
	SetupAnonymizerImageService()
	SetupOCRService()
	SetupSchedulerService()
	SetupDatasinkService()
	SetupRecognizerStoreService()
	SetupCache() cache.Cache
	AnalyzeItem(ctx context.Context, text string, template *types.AnalyzeTemplate) (*types.AnalyzeResponse, error)
	AnonymizeItem(ctx context.Context, analyzeResults []*types.AnalyzeResult, text string,
		anonymizeTemplate *types.AnonymizeTemplate) (*types.AnonymizeResponse, error)
	AnonymizeImageItem(ctx context.Context, image *types.Image, analyzeResults []*types.AnalyzeResult,
		anonymizeImageTypeEnum types.DetectionTypeEnum,
		anonymizeImageTemplate *types.AnonymizeImageTemplate) (*types.AnonymizeImageResponse, error)
	OcrItem(ctx context.Context, image *types.Image) (*types.OcrResponse, error)
	SendResultToDatasink(ctx context.Context, analyzeResults []*types.AnalyzeResult,
		anonymizeResults *types.AnonymizeResponse, path string) error
	ApplyStream(ctx context.Context, streamsJobRequest *types.StreamsJobRequest) (*types.StreamsJobResponse, error)
	ApplyScan(ctx context.Context, scanJobRequest *types.ScannerCronJobRequest) (*types.ScannerCronJobResponse, error)
	InitDatasink(ctx context.Context, datasinkTemplate *types.DatasinkTemplate) (*types.DatasinkResponse, error)
	CloseDatasink(ctx context.Context, datasinkTemplate *types.CompletionMessage) (*types.DatasinkResponse, error)

	InsertRecognizer(ctx context.Context, rec *types.PatternRecognizer) (*types.RecognizersStoreResponse, error)
	UpdateRecognizer(ctx context.Context, rec *types.PatternRecognizer) (*types.RecognizersStoreResponse, error)
	DeleteRecognizer(ctx context.Context, name string) (*types.RecognizersStoreResponse, error)
	GetRecognizer(ctx context.Context, name string) (*types.RecognizersGetResponse, error)
	GetAllRecognizers(ctx context.Context) (*types.RecognizersGetResponse, error)
	GetRecognizersHash(ctx context.Context) (*types.RecognizerHashResponse, error)
}

//TemplatesStore interface for template actions
type TemplatesStore interface {
	GetTemplate(project string, action string, id string) (string, error)
	InsertTemplate(project string, action string, id string, value string) error
	UpdateTemplate(project string, action string, id string, value string) error
	DeleteTemplate(project string, action string, id string) error
}

// Item interface represent the supported item's methods.
type Item interface {

	//GetUniqueID returns the scanned item unique id
	GetUniqueID() (string, error)

	//GetContent returns the content of the scanned item
	GetContent() (string, error)

	//GetPath returns the item path
	GetPath() string

	//IsContentTypeSupported returns if the item can be scanned.
	IsContentTypeSupported() error
}

// ConvertJSONToInterface convert Json to go Interface
func ConvertJSONToInterface(template string, convertTo interface{}) error {
	if template == "" {
		return fmt.Errorf("template is empty")
	}
	err := json.Unmarshal([]byte(template), &convertTo)
	return err
}

// ConvertInterfaceToJSON convert go interface to json
func ConvertInterfaceToJSON(template interface{}) (string, error) {
	b, err := json.Marshal(template)
	if err != nil {
		return "", err
	}
	return string(b), nil
}
