package anonymizeimage

import (
	"context"
	"fmt"

	types "github.com/Microsoft/presidio-genproto/golang"
	"github.com/Microsoft/presidio/pkg/presidio"
	store "github.com/Microsoft/presidio/presidio-api/cmd/presidio-api/api"
	"github.com/Microsoft/presidio/presidio-api/cmd/presidio-api/api/templates"
)

const maxImageSize = 4194304
const (
	jpeg = "image/jpeg"
	jpg  = "image/jpg"
	tiff = "image/tiff"
	tif  = "image/tif"
	png  = "image/png"
	bmp  = "image/bmp"
)

//AnonymizeImage anonymize image
func AnonymizeImage(ctx context.Context, api *store.API, anonymizeImageAPIRequest *types.AnonymizeImageApiRequest, project string) ([]byte, error) {

	err := validateFormat(anonymizeImageAPIRequest.Data, anonymizeImageAPIRequest.ImageType)
	if err != nil {
		return nil, err
	}

	err = validateAnonymizeImageTemplate(anonymizeImageAPIRequest)
	if err != nil {
		return nil, err
	}

	err = templates.GetTemplate(api, project, store.AnonymizeImage, anonymizeImageAPIRequest.AnonymizeImageTemplateId, &anonymizeImageAPIRequest.AnonymizeImageTemplate)
	if err != nil {
		return nil, err
	}

	image := &types.Image{
		Data: anonymizeImageAPIRequest.Data,
	}

	if anonymizeImageAPIRequest.DetectionType == types.DetectionTypeEnum_OCR {

		err = validateAnalyzeTemplate(anonymizeImageAPIRequest)
		if err != nil {
			return nil, err
		}

		err = templates.GetTemplate(api, project, store.Analyze, anonymizeImageAPIRequest.AnalyzeTemplateId, &anonymizeImageAPIRequest.AnalyzeTemplate)
		if err != nil {
			return nil, err
		}

		analyzeResults, err := applyPresidioOCR(ctx, api.Services, image, anonymizeImageAPIRequest.AnalyzeTemplate)
		if err != nil {
			return nil, err
		}
		image.ImageType = anonymizeImageAPIRequest.ImageType
		anonymizeResult, err := api.Services.AnonymizeImageItem(ctx, image, analyzeResults, anonymizeImageAPIRequest.DetectionType, anonymizeImageAPIRequest.AnonymizeImageTemplate)
		if err != nil {
			return nil, err
		}
		return anonymizeResult.Image.Data, nil
	}
	return nil, fmt.Errorf("Not method found")
}

func validateFormat(data []byte, imageType string) error {

	if data == nil {
		return fmt.Errorf("Image is empty or null")
	}
	if len(data) >= maxImageSize {
		return fmt.Errorf("File size is over 4MB")
	}
	if imageType == "" || (imageType != jpg &&
		imageType != jpeg &&
		imageType != tif &&
		imageType != tiff &&
		imageType != png &&
		imageType != bmp) {
		return fmt.Errorf("Image type is missing or wrong (image/jpg, image/jpeg, image/png, image/tiff, image/gif, image/bmp)")
	}
	return nil
}

func validateAnalyzeTemplate(anonymizeImageAPIRequest *types.AnonymizeImageApiRequest) error {
	if anonymizeImageAPIRequest.AnalyzeTemplateId == "" && anonymizeImageAPIRequest.AnalyzeTemplate == nil {
		return fmt.Errorf("Analyze template is missing or empty")
	} else if anonymizeImageAPIRequest.AnalyzeTemplate == nil {
		anonymizeImageAPIRequest.AnalyzeTemplate = &types.AnalyzeTemplate{}
	}
	return nil
}

func validateAnonymizeImageTemplate(anonymizeImageAPIRequest *types.AnonymizeImageApiRequest) error {
	if anonymizeImageAPIRequest.AnonymizeImageTemplateId == "" && anonymizeImageAPIRequest.AnonymizeImageTemplate == nil {
		return fmt.Errorf("Anonymize image template is missing or empty")
	} else if anonymizeImageAPIRequest.AnonymizeImageTemplate == nil {
		anonymizeImageAPIRequest.AnonymizeImageTemplate = &types.AnonymizeImageTemplate{}
	}
	return nil
}

func applyPresidioOCR(ctx context.Context, services presidio.ServicesAPI, image *types.Image, analyzeTemplate *types.AnalyzeTemplate) ([]*types.AnalyzeResult, error) {
	ocrRes, err := services.OcrItem(ctx, image)
	if err != nil {
		return nil, err
	}
	if ocrRes.Image.Text == "" {
		return nil, fmt.Errorf("No content found in image")

	}

	image.Text = ocrRes.Image.Text
	image.Boundingboxes = ocrRes.Image.Boundingboxes

	analyzeResponse, err := services.AnalyzeItem(ctx, ocrRes.Image.Text, analyzeTemplate)
	if err != nil {
		return nil, err

	}
	if analyzeResponse == nil || analyzeResponse.AnalyzeResults == nil {
		return nil, fmt.Errorf("No PII content found in image")

	}
	return analyzeResponse.AnalyzeResults, nil
}
