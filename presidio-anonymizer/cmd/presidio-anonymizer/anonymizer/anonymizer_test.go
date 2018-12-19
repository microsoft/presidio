package anonymizer

import (
	"testing"

	"github.com/stretchr/testify/assert"

	types "github.com/Microsoft/presidio-genproto/golang"
)

var testPlans = []struct {
	desc                    string
	text                    string
	expected                string
	analyzeResults          []*types.AnalyzeResult
	fieldTypeTransformation []*types.FieldTypeTransformation
}{{
	desc:     "Replace 1 Element",
	text:     "My phone number is 058-5559943",
	expected: "My phone number is <phone-number>",
	analyzeResults: []*types.AnalyzeResult{{
		Location: &types.Location{
			Start: 19,
			End:   30,
		},
		Field: &types.FieldTypes{
			Name: types.FieldTypesEnum_PHONE_NUMBER.String(),
		},
	}},
	fieldTypeTransformation: []*types.FieldTypeTransformation{{
		Fields: []*types.FieldTypes{{
			Name: types.FieldTypesEnum_PHONE_NUMBER.String(),
		}},
		Transformation: &types.Transformation{
			ReplaceValue: &types.ReplaceValue{
				NewValue: "<phone-number>",
			},
		},
	}},
}, {
	desc:     "Replace 2 Elements",
	text:     "My phone number is 058-5559943 and his number is 444-2341232",
	expected: "My phone number is <phone-number> and his number is <phone-number>",
	analyzeResults: []*types.AnalyzeResult{{
		Location: &types.Location{
			Start: 19,
			End:   30,
		},
		Field: &types.FieldTypes{
			Name: types.FieldTypesEnum_PHONE_NUMBER.String(),
		},
	}, {
		Location: &types.Location{
			Start: 49,
			End:   60,
		},
		Field: &types.FieldTypes{
			Name: types.FieldTypesEnum_PHONE_NUMBER.String(),
		},
	}},
	fieldTypeTransformation: []*types.FieldTypeTransformation{{
		Fields: []*types.FieldTypes{{
			Name: types.FieldTypesEnum_PHONE_NUMBER.String(),
		}},
		Transformation: &types.Transformation{
			ReplaceValue: &types.ReplaceValue{
				NewValue: "<phone-number>",
			},
		},
	}},
}, {
	desc:     "Replace 3 Mixed Elements",
	text:     "My phone number is 058-5559943 and credit card is 5555-5555-5555-5555 his number is 444-2341232",
	expected: "My phone number is <phone-number> and credit card is   his number is <phone-number>",
	analyzeResults: []*types.AnalyzeResult{{
		Location: &types.Location{
			Start: 19,
			End:   30,
		},
		Field: &types.FieldTypes{
			Name: types.FieldTypesEnum_PHONE_NUMBER.String(),
		},
	}, {
		Location: &types.Location{
			Start: 50,
			End:   69,
		},
		Field: &types.FieldTypes{
			Name: types.FieldTypesEnum_CREDIT_CARD.String(),
		},
	}, {
		Location: &types.Location{
			Start: 84,
			End:   95,
		},
		Field: &types.FieldTypes{
			Name: types.FieldTypesEnum_PHONE_NUMBER.String(),
		},
	}},
	fieldTypeTransformation: []*types.FieldTypeTransformation{{
		Fields: []*types.FieldTypes{{
			Name: types.FieldTypesEnum_PHONE_NUMBER.String(),
		}},
		Transformation: &types.Transformation{
			ReplaceValue: &types.ReplaceValue{
				NewValue: "<phone-number>",
			},
		},
	}, {
		Fields: []*types.FieldTypes{{
			Name: types.FieldTypesEnum_CREDIT_CARD.String(),
		}},
		Transformation: &types.Transformation{
			RedactValue: &types.RedactValue{},
		},
	}},
}, {
	desc:     "Hash 1 Element",
	text:     "My phone number is 058-5559943",
	expected: "My phone number is ae4d4488c82d30c560d5c761470d554f1db6c23b51b93f078d6f247611a2b0f3",
	analyzeResults: []*types.AnalyzeResult{{
		Location: &types.Location{
			Start: 19,
			End:   30,
		},
		Field: &types.FieldTypes{
			Name: types.FieldTypesEnum_PHONE_NUMBER.String(),
		},
	}},
	fieldTypeTransformation: []*types.FieldTypeTransformation{{
		Fields: []*types.FieldTypes{{
			Name: types.FieldTypesEnum_PHONE_NUMBER.String(),
		}},
		Transformation: &types.Transformation{
			HashValue: &types.HashValue{},
		},
	}},
}, {
	desc:     "Mask 1 Element",
	text:     "My credit card is 4061724061724061",
	expected: "My credit card is 40617240********",
	analyzeResults: []*types.AnalyzeResult{{
		Location: &types.Location{
			Start: 18,
			End:   34,
		},
		Field: &types.FieldTypes{
			Name: types.FieldTypesEnum_CREDIT_CARD.String(),
		},
	}},
	fieldTypeTransformation: []*types.FieldTypeTransformation{{
		Fields: []*types.FieldTypes{{
			Name: types.FieldTypesEnum_CREDIT_CARD.String(),
		}},
		Transformation: &types.Transformation{
			MaskValue: &types.MaskValue{
				MaskingCharacter: "*",
				CharsToMask:      8,
				FromEnd:          true,
			},
		},
	}},
}, {
	desc:     "Detect duplicate element",
	text:     "My name is danger and my location is Seattle",
	expected: "My name is <person> and my location is <location>",
	analyzeResults: []*types.AnalyzeResult{{
		Location: &types.Location{
			Start: 11,
			End:   17,
		},
		Score: 0.2,
		Field: &types.FieldTypes{
			Name: types.FieldTypesEnum_LOCATION.String(),
		},
	},
		{
			Location: &types.Location{
				Start: 11,
				End:   17,
			},
			Score: 0.85,
			Field: &types.FieldTypes{
				Name: types.FieldTypesEnum_PERSON.String(),
			},
		},
		{
			Location: &types.Location{
				Start: 11,
				End:   17,
			},
			Score: 0.50,
			Field: &types.FieldTypes{
				Name: types.FieldTypesEnum_NRP.String(),
			},
		},
		{
			Location: &types.Location{
				Start: 37,
				End:   44,
			},
			Score: 0.35,
			Field: &types.FieldTypes{
				Name: types.FieldTypesEnum_DATE_TIME.String(),
			},
		},
		{
			Location: &types.Location{
				Start: 37,
				End:   44,
			},
			Score: 0.65,
			Field: &types.FieldTypes{
				Name: types.FieldTypesEnum_LOCATION.String(),
			},
		}},
	fieldTypeTransformation: []*types.FieldTypeTransformation{{
		Fields: []*types.FieldTypes{{
			Name: types.FieldTypesEnum_PERSON.String(),
		}},
		Transformation: &types.Transformation{
			ReplaceValue: &types.ReplaceValue{
				NewValue: "<person>",
			},
		},
	}, {
		Fields: []*types.FieldTypes{{
			Name: types.FieldTypesEnum_LOCATION.String(),
		}},
		Transformation: &types.Transformation{
			ReplaceValue: &types.ReplaceValue{
				NewValue: "<location>",
			},
		},
	}, {
		Fields: []*types.FieldTypes{{
			Name: types.FieldTypesEnum_NRP.String(),
		}},
		Transformation: &types.Transformation{
			ReplaceValue: &types.ReplaceValue{
				NewValue: "<nrp>",
			},
		},
	}, {
		Fields: []*types.FieldTypes{{
			Name: types.FieldTypesEnum_DATE_TIME.String(),
		}},
		Transformation: &types.Transformation{
			ReplaceValue: &types.ReplaceValue{
				NewValue: "<date>",
			},
		},
	}},
},
}

func TestPlan(t *testing.T) {
	for _, plan := range testPlans {
		t.Logf("Testing %s", plan.desc)

		anonymizerTemplate := types.AnonymizeTemplate{
			FieldTypeTransformations: plan.fieldTypeTransformation,
		}
		output, err := ApplyAnonymizerTemplate(plan.text, plan.analyzeResults, &anonymizerTemplate)
		if err != nil {
			assert.Error(t, err)
		}
		assert.Equal(t, plan.expected, output)
	}
}
