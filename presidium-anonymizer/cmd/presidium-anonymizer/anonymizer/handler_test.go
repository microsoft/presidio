package anonymizer

import (
	"testing"

	"github.com/stretchr/testify/assert"

	message_types "github.com/presidium-io/presidium/pkg/types"
)

func TestReplace1Element(t *testing.T) {

	text := "My phone number is 058-5559943"
	expected := "My phone number is <phone-number>"

	replace := message_types.ReplaceValue{
		NewValue: "<phone-number>",
	}
	var fieldTypes = make([]*message_types.FieldType, 0)
	fieldTypes = append(fieldTypes, &message_types.PhoneNumber)

	transformation := message_types.Transformation{
		ReplaceValue: &replace,
	}
	//Create infotype transformation
	fieldTypeTransformation := message_types.FieldTypeTransformation{
		FieldTypes:     fieldTypes,
		Transformation: &transformation,
	}

	var fieldTypeTransformationArray = make([]*message_types.FieldTypeTransformation, 0)
	fieldTypeTransformationArray = append(fieldTypeTransformationArray, &fieldTypeTransformation)

	config := message_types.Configuration{
		FieldTypeTransformations: fieldTypeTransformationArray,
	}

	anonymizerTemplate := message_types.AnonymizeTemplate{
		Name:          message_types.PhoneNumber.Name,
		DisplayName:   "Phone number",
		Configuration: &config,
	}

	var result message_types.Result
	result.Location = &message_types.Location{
		Start: 19,
		End:   30,
	}
	result.Value = "058-5559943"
	result.FieldType = message_types.PhoneNumber.Name

	var resultArray = make([]*message_types.Result, 0)
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

	replace := message_types.ReplaceValue{
		NewValue: "<phone-number>",
	}
	var fieldTypes = make([]*message_types.FieldType, 0)
	fieldTypes = append(fieldTypes, &message_types.PhoneNumber)

	transformation := message_types.Transformation{
		ReplaceValue: &replace,
	}
	//Create infotype transformation
	fieldTypeTransformation := message_types.FieldTypeTransformation{
		FieldTypes:     fieldTypes,
		Transformation: &transformation,
	}

	var fieldTypeTransformationArray = make([]*message_types.FieldTypeTransformation, 0)
	fieldTypeTransformationArray = append(fieldTypeTransformationArray, &fieldTypeTransformation)

	config := message_types.Configuration{
		FieldTypeTransformations: fieldTypeTransformationArray,
	}

	anonymizerTemplate := message_types.AnonymizeTemplate{
		Name:          message_types.PhoneNumber.Name,
		DisplayName:   "Phone number",
		Configuration: &config,
	}

	var result1 message_types.Result
	result1.Location = &message_types.Location{
		Start: 19,
		End:   30,
	}
	result1.Value = "058-5559943"
	result1.FieldType = message_types.PhoneNumber.Name

	var result2 message_types.Result
	result2.Location = &message_types.Location{
		Start: 49,
		End:   60,
	}
	result2.Value = "444-2341232"
	result2.FieldType = message_types.PhoneNumber.Name

	var resultArray = make([]*message_types.Result, 0)
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

	replace := message_types.ReplaceValue{
		NewValue: "<phone-number>",
	}
	var fieldTypes1 = make([]*message_types.FieldType, 0)
	fieldTypes1 = append(fieldTypes1, &message_types.PhoneNumber)

	transformation1 := message_types.Transformation{
		ReplaceValue: &replace,
	}
	//Create infotype transformation
	fieldTypeTransformation1 := message_types.FieldTypeTransformation{
		FieldTypes:     fieldTypes1,
		Transformation: &transformation1,
	}

	redact := message_types.RedactValue{}

	var fieldTypes2 = make([]*message_types.FieldType, 0)
	fieldTypes2 = append(fieldTypes2, &message_types.CreditCard)

	transformation2 := message_types.Transformation{
		RedactValue: &redact,
	}
	//Create infotype transformation
	fieldTypeTransformation2 := message_types.FieldTypeTransformation{
		FieldTypes:     fieldTypes2,
		Transformation: &transformation2,
	}

	var fieldTypeTransformationArray = make([]*message_types.FieldTypeTransformation, 0)
	fieldTypeTransformationArray = append(fieldTypeTransformationArray, &fieldTypeTransformation1, &fieldTypeTransformation2)

	config := message_types.Configuration{
		FieldTypeTransformations: fieldTypeTransformationArray,
	}

	anonymizerTemplate := message_types.AnonymizeTemplate{
		Name:          message_types.PhoneNumber.Name,
		DisplayName:   "Phone number",
		Configuration: &config,
	}

	var result1 message_types.Result
	result1.Location = &message_types.Location{
		Start: 19,
		End:   30,
	}
	result1.Value = "058-5559943"
	result1.FieldType = message_types.PhoneNumber.Name

	var result2 message_types.Result
	result2.Location = &message_types.Location{
		Start: 50,
		End:   69,
	}
	result2.Value = "5555-5555-5555-5555"
	result2.FieldType = message_types.CreditCard.Name

	var result3 message_types.Result
	result3.Location = &message_types.Location{
		Start: 84,
		End:   95,
	}
	result3.Value = "444-2341232"
	result3.FieldType = message_types.PhoneNumber.Name

	var resultArray = make([]*message_types.Result, 0)

	resultArray = append(resultArray, &result1, &result2, &result3)

	output, err := ApplyAnonymizerTemplate(text, resultArray, &anonymizerTemplate)
	if err != nil {
		assert.Error(t, err)
	}

	assert.Equal(t, expected, output)
}
