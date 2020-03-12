// +build integration

package tests

import (
	"encoding/json"
	"io/ioutil"

	"github.com/stretchr/testify/assert"

	types "github.com/Microsoft/presidio-genproto/golang"
	"github.com/Microsoft/presidio/functional-tests/common"
	"github.com/Microsoft/presidio/presidio-anonymizer-image/cmd/presidio-anonymizer-image/anonymizer"

	"testing"
)

func TestAnonymizeImage(t *testing.T) {

	content, err := ioutil.ReadFile(common.TestDataPath + "ocr-test.png")
	assert.NoError(t, err)

	jcontent, err := ioutil.ReadFile(common.TestDataPath + "ocr-result.json")
	assert.NoError(t, err)

	image := &types.Image{
		Data:      content,
		ImageType: "image/png",
	}
	json.Unmarshal(jcontent, image)

	results := []*types.AnalyzeResult{
		{
			Location: &types.Location{
				Start: 27, End: 40,
			},
		},
		{
			Location: &types.Location{
				Start: 294, End: 311,
			},
		},
		{
			Location: &types.Location{
				Start: 323, End: 337,
			},
		},
		{
			Location: &types.Location{
				Start: 749, End: 771,
			},
		},
		{
			Location: &types.Location{
				Start: 758, End: 771,
			},
		},
	}

	template := &types.AnonymizeImageTemplate{
		FieldTypeGraphics: []*types.FieldTypeGraphic{
			{
				Graphic: &types.Graphic{
					FillColorValue: &types.FillColorValue{
						Red:   0,
						Green: 0,
						Blue:  0,
					},
				},
			},
		},
	}

	result, err := anonymizer.AnonymizeImage(image, types.DetectionTypeEnum_OCR, results, template)
	assert.NoError(t, err)
	assert.NotNil(t, result)

	savedOutputImage, err := ioutil.ReadFile(common.TestDataPath + "ocr-result.png")
	assert.NoError(t, err)

	assert.Equal(t, len(savedOutputImage), len(result.Data))

}
