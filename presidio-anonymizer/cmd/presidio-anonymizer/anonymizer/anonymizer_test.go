package anonymizer

import (
	"testing"

	"encoding/json"

	"github.com/stretchr/testify/assert"

	types "github.com/Microsoft/presidio-genproto/golang"
)

var testPlans = []struct {
	desc                    string
	text                    string
	expected                string
	analyzeResults          []*types.AnalyzeResult
	fieldTypeTransformation []*types.FieldTypeTransformation
	defaultTransformation   *types.Transformation
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
	expected: "My name is <person> and my location is <loc>",
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
			Score: 0.65,
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
				NewValue: "<loc>",
			},
		},
	}, {
		Fields: []*types.FieldTypes{{
			Name: types.FieldTypesEnum_NRP.String(),
		}},
		Transformation: &types.Transformation{
			ReplaceValue: &types.ReplaceValue{
				NewValue: "<nrp group>",
			},
		},
	}, {
		Fields: []*types.FieldTypes{{
			Name: types.FieldTypesEnum_DATE_TIME.String(),
		}},
		Transformation: &types.Transformation{
			ReplaceValue: &types.ReplaceValue{
				NewValue: "<thisisdate>",
			},
		},
	}},
},
	// Replace 1 custom field with a specific transformation for this kind of field
	{
		desc:     "Replace 1 custom field",
		text:     "My custom field is myvalue",
		expected: "My custom field is <CUSTOM_REPLACE>",
		analyzeResults: []*types.AnalyzeResult{{
			Location: &types.Location{
				Start: 19,
				End:   26,
			},
			Field: &types.FieldTypes{
				Name: "customtype",
			},
		}},
		fieldTypeTransformation: []*types.FieldTypeTransformation{{
			Fields: []*types.FieldTypes{{
				Name: "customtype",
			}},
			Transformation: &types.Transformation{
				ReplaceValue: &types.ReplaceValue{
					NewValue: "<CUSTOM_REPLACE>",
				},
			},
		}},
	},
	// Replace 1 custom field with the basic default transformation
	{
		desc:     "Replace 1 undeclared field using default transformation",
		text:     "My undeclared field is myvalue",
		expected: "My undeclared field is <CUSTOMTYPE>",
		analyzeResults: []*types.AnalyzeResult{{
			Location: &types.Location{
				Start: 23,
				End:   30,
			},
			Field: &types.FieldTypes{
				Name: "customtype",
			},
		}},
	},
	// Replace two custom fields with a transformation which was declared for ALL fields
	{
		desc:     "Replace 2 custom fields",
		text:     "My custom field is myvalue and myvalue2",
		expected: "My custom field is <CUSTOM_REPLACE> and <CUSTOM_REPLACE>",
		analyzeResults: []*types.AnalyzeResult{{
			Location: &types.Location{
				Start: 19,
				End:   26,
			},
			Field: &types.FieldTypes{
				Name: "customtype",
			},
		},
			{
				Location: &types.Location{
					Start: 31,
					End:   39,
				},
				Field: &types.FieldTypes{
					Name: "customtype2",
				},
			}},
		fieldTypeTransformation: []*types.FieldTypeTransformation{{
			Transformation: &types.Transformation{
				ReplaceValue: &types.ReplaceValue{
					NewValue: "<CUSTOM_REPLACE>",
				},
			},
		}},
	},
	// Replace 1 custom field with a specific transformation. Replace the second with a default transformation
	{
		desc:     "Replace 2 custom fields, some with provided default transformation",
		text:     "My custom field is myvalue and myvalue2",
		expected: "My custom field is   and <CUSTOM_REPLACE>",
		analyzeResults: []*types.AnalyzeResult{{
			Location: &types.Location{
				Start: 19,
				End:   26,
			},
			Field: &types.FieldTypes{
				Name: "customtype",
			},
		},
			{
				Location: &types.Location{
					Start: 31,
					End:   39,
				},
				Field: &types.FieldTypes{
					Name: "customtype2",
				},
			}},
		defaultTransformation: &types.Transformation{
			RedactValue: &types.RedactValue{}},
		fieldTypeTransformation: []*types.FieldTypeTransformation{{
			Fields: []*types.FieldTypes{{
				Name: "customtype2",
			}},
			Transformation: &types.Transformation{
				ReplaceValue: &types.ReplaceValue{
					NewValue: "<CUSTOM_REPLACE>",
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
			DefaultTransformation:    plan.defaultTransformation,
		}
		output, err := AnonymizeText(plan.text, plan.analyzeResults, &anonymizerTemplate)
		assert.NoError(t, err)
		assert.Equal(t, plan.expected, output)
	}
}

func TestMultipleValuesBasedOnJSON(t *testing.T) {
	var analyzeResultsJSON = `[{"text":"4095-2609-9393-4932","field":{"name":"CREDIT_CARD"},"score":1,"location":{"start":76,"end":95,"length":19}},{"text":"16Yeky6GMjeNkAiNcBY7ZhrLoMSgg1BoyZ","field":{"name":"CRYPTO"},"score":1,"location":{"start":118,"end":152,"length":34}},{"text":"September 18","field":{"name":"DATE_TIME"},"score":0.85,"location":{"start":167,"end":179,"length":12}},{"text":"microsoft.com","field":{"name":"DOMAIN_NAME"},"score":1,"location":{"start":192,"end":205,"length":13}},{"text":"test@presidio.site","field":{"name":"EMAIL_ADDRESS"},"score":1,"location":{"start":225,"end":243,"length":18}},{"text":"presidio.site","field":{"name":"DOMAIN_NAME"},"score":1,"location":{"start":230,"end":243,"length":13}},{"text":"IL150120690000003111111","field":{"name":"IBAN_CODE"},"score":1,"location":{"start":254,"end":277,"length":23}},{"text":"192.168.0.1","field":{"name":"IP_ADDRESS"},"score":0.95,"location":{"start":286,"end":297,"length":11}},{"text":"David Johnson","field":{"name":"PERSON"},"score":0.85,"location":{"start":315,"end":328,"length":13}},{"text":"2854567876542","field":{"name":"US_BANK_NUMBER"},"score":0.6,"location":{"start":348,"end":361,"length":13}},{"text":"H12234567","field":{"name":"US_DRIVER_LICENSE"},"score":0.65,"location":{"start":389,"end":398,"length":9}},{"text":"912803456","field":{"name":"US_BANK_NUMBER"},"score":0.05,"location":{"start":414,"end":423,"length":9}},{"text":"912803456","field":{"name":"US_PASSPORT"},"score":0.6,"location":{"start":414,"end":423,"length":9}},{"text":"912803456","field":{"name":"US_ITIN"},"score":0.3,"location":{"start":414,"end":423,"length":9}},{"text":"(212) 555-1234","field":{"name":"PHONE_NUMBER"},"score":1,"location":{"start":442,"end":456,"length":14}},{"text":"078-05-1120","field":{"name":"US_SSN"},"score":0.85,"location":{"start":486,"end":497,"length":11}},{"text":"cla.microsoft.com","field":{"name":"DOMAIN_NAME"},"score":1,"location":{"start":761,"end":778,"length":17}},{"text":"opencode@microsoft.com","field":{"name":"EMAIL_ADDRESS"},"score":1,"location":{"start":1193,"end":1215,"length":22}},{"text":"microsoft.com","field":{"name":"DOMAIN_NAME"},"score":1,"location":{"start":1202,"end":1215,"length":13}}]`
	analyzeResults := []*types.AnalyzeResult{}
	err := json.Unmarshal([]byte(analyzeResultsJSON), &analyzeResults)
	assert.NoError(t, err)

	var anonymizeTemplateJSON = `{"fieldTypeTransformations":[{"fields":[{"name":"DOMAIN_NAME"}],"transformation":{"replaceValue":{"newValue":"<DOMAIN_NAME>"}}},{"fields":[{"name":"PERSON"}],"transformation":{"replaceValue":{"newValue":"<PERSON>"}}},{"fields":[{"name":"US_BANK_NUMBER"}],"transformation":{"replaceValue":{"newValue":"<US_BANK_NUMBER>"}}},{"fields":[{"name":"CRYPTO"}],"transformation":{"replaceValue":{"newValue":"<CRYPTO>"}}},{"fields":[{"name":"EMAIL_ADDRESS"}],"transformation":{"replaceValue":{"newValue":"<EMAIL_ADDRESS>"}}},{"fields":[{"name":"US_PASSPORT"}],"transformation":{"replaceValue":{"newValue":"<US_PASSPORT>"}}},{"fields":[{"name":"DATE_TIME"}],"transformation":{"replaceValue":{"newValue":"<DATE_TIME>"}}},{"fields":[{"name":"IP_ADDRESS"}],"transformation":{"replaceValue":{"newValue":"<IP_ADDRESS>"}}},{"fields":[{"name":"NRP"}],"transformation":{"replaceValue":{"newValue":"<NRP>"}}},{"fields":[{"name":"UK_NHS"}],"transformation":{"replaceValue":{"newValue":"<UK_NHS>"}}},{"fields":[{"name":"CREDIT_CARD"}],"transformation":{"replaceValue":{"newValue":"<CREDIT_CARD>"}}},{"fields":[{"name":"IBAN_CODE"}],"transformation":{"replaceValue":{"newValue":"<IBAN_CODE>"}}},{"fields":[{"name":"LOCATION"}],"transformation":{"replaceValue":{"newValue":"<LOCATION>"}}},{"fields":[{"name":"PHONE_NUMBER"}],"transformation":{"replaceValue":{"newValue":"<PHONE_NUMBER>"}}},{"fields":[{"name":"US_DRIVER_LICENSE"}],"transformation":{"replaceValue":{"newValue":"<US_DRIVER_LICENSE>"}}},{"fields":[{"name":"US_ITIN"}],"transformation":{"replaceValue":{"newValue":"<US_ITIN>"}}},{"fields":[{"name":"US_SSN"}],"transformation":{"replaceValue":{"newValue":"<US_SSN>"}}}]}`
	anonymizerTemplate := types.AnonymizeTemplate{}
	err = json.Unmarshal([]byte(anonymizeTemplateJSON), &anonymizerTemplate)
	assert.NoError(t, err)

	text := `Here are a few examples of entities we currently support:

    Credit card: 4095-2609-9393-4932
    Crypto wallet id: 16Yeky6GMjeNkAiNcBY7ZhrLoMSgg1BoyZ
    DateTime: September 18
    Domain: microsoft.com
    Email address: test@presidio.site
    IBAN: IL150120690000003111111
    IP: 192.168.0.1
    Person name: David Johnson

    Bank account: 2854567876542
    Driver license number: H12234567 
    Passport: 912803456
    Phone number: (212) 555-1234.
    Social security number: 078-05-1120

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.
When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the 
PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the Microsoft Open Source Code of Conduct. For more information see the Code of Conduct FAQ or contact 
opencode@microsoft.com with any additional questions or comments.`

	output, err := AnonymizeText(text, analyzeResults, &anonymizerTemplate)
	assert.NoError(t, err)

	expected := `Here are a few examples of entities we currently support:

    Credit card: <CREDIT_CARD>
    Crypto wallet id: <CRYPTO>
    DateTime: <DATE_TIME>
    Domain: <DOMAIN_NAME>
    Email address: <EMAIL_ADDRESS>
    IBAN: <IBAN_CODE>
    IP: <IP_ADDRESS>
    Person name: <PERSON>

    Bank account: <US_BANK_NUMBER>
    Driver license number: <US_DRIVER_LICENSE> 
    Passport: <US_PASSPORT>
    Phone number: <PHONE_NUMBER>.
    Social security number: <US_SSN>

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://<DOMAIN_NAME>.
When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the 
PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the Microsoft Open Source Code of Conduct. For more information see the Code of Conduct FAQ or contact 
<EMAIL_ADDRESS> with any additional questions or comments.`

	assert.Equal(t, expected, output)
}
