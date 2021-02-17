from presidio_anonymizer.entities import AnonymizersDTO, AnonymizerDTO


def test_given_anonymizers_dto_then_we_get_correct_anonymizer_with_default():
    phone_number_dto = AnonymizerDTO("fpe", {})
    default_dto = AnonymizerDTO("redact", {})
    anonymizer_dto = AnonymizersDTO({"PHONE_NUMBER": phone_number_dto,
                                     "DEFAULT": default_dto,
                                     "NUMBER": default_dto,
                                     "PHONE_NUM": default_dto})
    assert anonymizer_dto.get_anonymizer("PHONE_NUMBER") == phone_number_dto
    assert anonymizer_dto.get_anonymizer("NONE_EXISTING") == default_dto


def test_given_anonymizers_dto_then_we_get_correct_anonymizer_without_default():
    phone_number_dto = AnonymizerDTO("fpe", {})
    anonymizer_dto = AnonymizersDTO({"PHONE_NUMBER": phone_number_dto})
    assert anonymizer_dto.get_anonymizer("PHONE_NUMBER") == phone_number_dto
    assert anonymizer_dto.get_anonymizer("NONE_EXISTING") == AnonymizerDTO("replace",
                                                                           {})
