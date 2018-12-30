package tests

import (
	"encoding/json"
	types "github.com/Microsoft/presidio-genproto/golang"
	"github.com/Microsoft/presidio/presidio-anonymizer-image/cmd/presidio-anonymizer-image/anonymizer"
	"github.com/stretchr/testify/assert"
	"io/ioutil"
	"os"
	"testing"
)

func TestAnonymizeImage(t *testing.T) {

	content, err := ioutil.ReadFile("./testdata/ocr-test.png")
	assert.NoError(t, err)

	jcontent, err := ioutil.ReadFile("./testdata/ocr-result.json")
	assert.NoError(t, err)

	image := &types.Image{
		Data: content,
	}
	json.Unmarshal(jcontent, image)

	results := []*types.AnalyzeResult{
		&types.AnalyzeResult{
			Location: &types.Location{
				Start: 35, End: 49,
			},
		},
		&types.AnalyzeResult{
			Location: &types.Location{
				Start: 66, End: 81,
			},
		},
		&types.AnalyzeResult{
			Location: &types.Location{
				Start: 102, End: 118,
			},
		},
		&types.AnalyzeResult{
			Location: &types.Location{
				Start: 137, End: 144,
			},
		},
	}

	template := &types.AnonymizeImageTemplate{
		FieldTypeGraphics: []*types.FieldTypeGraphic{
			&types.FieldTypeGraphic{
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

	result, err := anonymizer.AnonymizeImage(image, types.AnonymizeImageTypeEnum_OCR, results, template)
	assert.NoError(t, err)
	assert.NotNil(t, result)
	// fo, err := os.Create("output.png")
	// fo.Write(result.Data)
	// fo.Sync()
	// fo.Close()

}
