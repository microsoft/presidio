package anonymizer

import (
	"testing"

	"github.com/stretchr/testify/assert"

	types "github.com/Microsoft/presidio-genproto/golang"
)

func TestReplace1Element(t *testing.T) {

	text := "My phone number is 058-5559943"
	expected := "My phone number is <phone-number>"

	replace := types.ReplaceValue{
		NewValue: "<phone-number>",
	}
	var fieldTypes = make([]*types.FieldTypes, 0)

	fieldTypes = append(fieldTypes, &types.FieldTypes{Name: types.FieldTypesEnum_PHONE_NUMBER.String()})

	transformation := types.Transformation{
		ReplaceValue: &replace,
	}
	//Create infotype transformation
	fieldTypeTransformation := types.FieldTypeTransformation{
		Fields:         fieldTypes,
		Transformation: &transformation,
	}

	var fieldTypeTransformationArray = make([]*types.FieldTypeTransformation, 0)
	fieldTypeTransformationArray = append(fieldTypeTransformationArray, &fieldTypeTransformation)

	anonymizerTemplate := types.AnonymizeTemplate{
		FieldTypeTransformations: fieldTypeTransformationArray,
	}

	var result types.AnalyzeResult
	result.Location = &types.Location{
		Start: 19,
		End:   30,
	}
	result.Text = "058-5559943"
	result.Field = &types.FieldTypes{Name: types.FieldTypesEnum_PHONE_NUMBER.String()}

	var resultArray = make([]*types.AnalyzeResult, 0)
	resultArray = append(resultArray, &result)

	output, err := ApplyAnonymizerTemplate(text, resultArray, &anonymizerTemplate)
	if err != nil {
		assert.Error(t, err)
	}
	assert.Equal(t, expected, output)
}

func TestReplace2Elements(t *testing.T) {

	text := "My phone number is 058-5559943 and his number is 444-2341232"
	expected := "My phone number is <phone-number> and his number is <phone-number>"

	replace := types.ReplaceValue{
		NewValue: "<phone-number>",
	}
	var fieldTypes = make([]*types.FieldTypes, 0)
	fieldTypes = append(fieldTypes, &types.FieldTypes{Name: types.FieldTypesEnum_PHONE_NUMBER.String()})

	transformation := types.Transformation{
		ReplaceValue: &replace,
	}
	//Create infotype transformation
	fieldTypeTransformation := types.FieldTypeTransformation{
		Fields:         fieldTypes,
		Transformation: &transformation,
	}

	var fieldTypeTransformationArray = make([]*types.FieldTypeTransformation, 0)
	fieldTypeTransformationArray = append(fieldTypeTransformationArray, &fieldTypeTransformation)

	anonymizerTemplate := types.AnonymizeTemplate{
		FieldTypeTransformations: fieldTypeTransformationArray,
	}

	var result1 types.AnalyzeResult
	result1.Location = &types.Location{
		Start: 19,
		End:   30,
	}
	result1.Text = "058-5559943"
	result1.Field = &types.FieldTypes{Name: types.FieldTypesEnum_PHONE_NUMBER.String()}

	var result2 types.AnalyzeResult
	result2.Location = &types.Location{
		Start: 49,
		End:   60,
	}
	result2.Text = "444-2341232"
	result2.Field = &types.FieldTypes{Name: types.FieldTypesEnum_PHONE_NUMBER.String()}

	var resultArray = make([]*types.AnalyzeResult, 0)
	resultArray = append(resultArray, &result1, &result2)

	output, err := ApplyAnonymizerTemplate(text, resultArray, &anonymizerTemplate)
	if err != nil {
		assert.Error(t, err)
	}
	assert.Equal(t, output, expected)
}

func TestReplace3Elements(t *testing.T) {

	text := "My phone number is 058-5559943 and credit card is 5555-5555-5555-5555 his number is 444-2341232"
	expected := "My phone number is <phone-number> and credit card is   his number is <phone-number>"

	replace := types.ReplaceValue{
		NewValue: "<phone-number>",
	}
	var fieldTypes1 = make([]*types.FieldTypes, 0)
	fieldTypes1 = append(fieldTypes1, &types.FieldTypes{Name: types.FieldTypesEnum_PHONE_NUMBER.String()})

	transformation1 := types.Transformation{
		ReplaceValue: &replace,
	}
	//Create infotype transformation
	fieldTypeTransformation1 := types.FieldTypeTransformation{
		Fields:         fieldTypes1,
		Transformation: &transformation1,
	}

	redact := types.RedactValue{}

	var fieldTypes2 = make([]*types.FieldTypes, 0)
	fieldTypes2 = append(fieldTypes2, &types.FieldTypes{Name: types.FieldTypesEnum_CREDIT_CARD.String()})

	transformation2 := types.Transformation{
		RedactValue: &redact,
	}
	//Create infotype transformation
	fieldTypeTransformation2 := types.FieldTypeTransformation{
		Fields:         fieldTypes2,
		Transformation: &transformation2,
	}

	var fieldTypeTransformationArray = make([]*types.FieldTypeTransformation, 0)
	fieldTypeTransformationArray = append(fieldTypeTransformationArray, &fieldTypeTransformation1, &fieldTypeTransformation2)

	anonymizerTemplate := types.AnonymizeTemplate{
		FieldTypeTransformations: fieldTypeTransformationArray,
	}

	var result1 types.AnalyzeResult
	result1.Location = &types.Location{
		Start: 19,
		End:   30,
	}
	result1.Text = "058-5559943"
	result1.Field = &types.FieldTypes{Name: types.FieldTypesEnum_PHONE_NUMBER.String()}

	var result2 types.AnalyzeResult
	result2.Location = &types.Location{
		Start: 50,
		End:   69,
	}
	result2.Text = "5555-5555-5555-5555"
	result2.Field = &types.FieldTypes{Name: types.FieldTypesEnum_CREDIT_CARD.String()}

	var result3 types.AnalyzeResult
	result3.Location = &types.Location{
		Start: 84,
		End:   95,
	}
	result3.Text = "444-2341232"
	result3.Field = &types.FieldTypes{Name: types.FieldTypesEnum_PHONE_NUMBER.String()}

	var resultArray = make([]*types.AnalyzeResult, 0)

	resultArray = append(resultArray, &result1, &result2, &result3)

	output, err := ApplyAnonymizerTemplate(text, resultArray, &anonymizerTemplate)
	if err != nil {
		assert.Error(t, err)
	}

	assert.Equal(t, expected, output)
}
func TestHash1Element(t *testing.T) {

	text := "My phone number is 058-5559943"
	expected := "My phone number is ae4d4488c82d30c560d5c761470d554f1db6c23b51b93f078d6f247611a2b0f3"

	hash := types.HashValue{}
	var fieldTypes = make([]*types.FieldTypes, 0)

	fieldTypes = append(fieldTypes, &types.FieldTypes{Name: types.FieldTypesEnum_PHONE_NUMBER.String()})

	transformation := types.Transformation{
		HashValue: &hash,
	}
	//Create infotype transformation
	fieldTypeTransformation := types.FieldTypeTransformation{
		Fields:         fieldTypes,
		Transformation: &transformation,
	}

	var fieldTypeTransformationArray = make([]*types.FieldTypeTransformation, 0)
	fieldTypeTransformationArray = append(fieldTypeTransformationArray, &fieldTypeTransformation)

	anonymizerTemplate := types.AnonymizeTemplate{
		FieldTypeTransformations: fieldTypeTransformationArray,
	}

	var result types.AnalyzeResult
	result.Location = &types.Location{
		Start: 19,
		End:   30,
	}
	result.Text = "058-5559943"
	result.Field = &types.FieldTypes{Name: types.FieldTypesEnum_PHONE_NUMBER.String()}

	var resultArray = make([]*types.AnalyzeResult, 0)
	resultArray = append(resultArray, &result)

	output, err := ApplyAnonymizerTemplate(text, resultArray, &anonymizerTemplate)
	if err != nil {
		assert.Error(t, err)
	}
	assert.Equal(t, expected, output)
}

func TestMask1Element(t *testing.T) {
	text := "My credit card is 4061724061724061"
	expected := "My credit card is 40617240********"

	mask := types.MaskValue{
		MaskingCharacter: "*",
		CharsToMask:      8,
		FromEnd:          true,
	}
	var fieldTypes = make([]*types.FieldTypes, 0)

	fieldTypes = append(fieldTypes, &types.FieldTypes{Name: types.FieldTypesEnum_CREDIT_CARD.String()})

	transformation := types.Transformation{
		MaskValue: &mask,
	}
	//Create infotype transformation
	fieldTypeTransformation := types.FieldTypeTransformation{
		Fields:         fieldTypes,
		Transformation: &transformation,
	}

	var fieldTypeTransformationArray = make([]*types.FieldTypeTransformation, 0)
	fieldTypeTransformationArray = append(fieldTypeTransformationArray, &fieldTypeTransformation)

	anonymizerTemplate := types.AnonymizeTemplate{
		FieldTypeTransformations: fieldTypeTransformationArray,
	}

	var result types.AnalyzeResult
	result.Location = &types.Location{
		Start: 18,
		End:   34,
	}
	result.Text = "4061724061724061"
	result.Field = &types.FieldTypes{Name: types.FieldTypesEnum_CREDIT_CARD.String()}

	var resultArray = make([]*types.AnalyzeResult, 0)
	resultArray = append(resultArray, &result)

	output, err := ApplyAnonymizerTemplate(text, resultArray, &anonymizerTemplate)
	if err != nil {
		assert.Error(t, err)
	}
	assert.Equal(t, expected, output)
}
