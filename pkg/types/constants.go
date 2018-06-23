package types

var (
	//PhoneNumber ...
	PhoneNumber = FieldType{Name: "PHONE_NUMBER",
		LanguageCode: ""}

	//CreditCard ...
	CreditCard = FieldType{Name: "CREDIT_CARD", LanguageCode: ""}
)

//FieldTypes description
var FieldTypes = [2]string{PhoneNumber.Name, CreditCard.Name}
