from presidio_anonymizer import BatchAnonymizerEngine
from presidio_analyzer import RecognizerResult, DictAnalyzerResult
from presidio_anonymizer.entities import OperatorConfig


texts = ['John', 'Jill', 'Jack']
recognizer_results_list = [[RecognizerResult('PERSON', 0, 4, 0.85)],
                           [RecognizerResult('PERSON', 0, 4, 0.85)],
                           [RecognizerResult('PERSON', 0, 4, 0.85)]]
analyzer_results = [DictAnalyzerResult(key='name',
                                       value=texts,
                                       recognizer_results=recognizer_results_list)]


def test_given_analyzer_result_we_anonymize_dict_correctly():
    engine = BatchAnonymizerEngine()
    anonymized_results = engine.anonymize_dict(analyzer_results)
    assert anonymized_results == {'name': ['<PERSON>', '<PERSON>', '<PERSON>']}


def test_given_analyzer_result_we_anonymize_list_correctly():
    engine = BatchAnonymizerEngine()
    anonymized_results = engine.anonymize_list(
      texts=texts, recognizer_results_list=recognizer_results_list)
    assert anonymized_results == ['<PERSON>', '<PERSON>', '<PERSON>']


def test_given_empty_recognizers_than_we_return_text_unchanged():
    empty_analyzer_results = [DictAnalyzerResult(key='name',
                                                 value=texts,
                                                 recognizer_results=[])]
    engine = BatchAnonymizerEngine()
    anonymized_results = engine.anonymize_dict(empty_analyzer_results)
    assert anonymized_results == {'name': ['John', 'Jill', 'Jack']}


def test_given_complex_analyzer_result_we_anonymize_dict_correctly():
    analyzer_results = [DictAnalyzerResult(key='name',
                                           value=texts,
                                           recognizer_results=recognizer_results_list),
        DictAnalyzerResult(key='comments',
          value=['called him yesterday to confirm he requested to call back in 2 days',
          'accepted the offer license number AC432223',
          'need to call him at phone number 212-555-5555'],
          recognizer_results=[[RecognizerResult('DATE_TIME', 11, 20, 0.85), 
          RecognizerResult('DATE_TIME', 61, 67, 0.85)],
                  [RecognizerResult('US_DRIVER_LICENSE', 34, 42, 0.6499999999999999)],
                  [RecognizerResult('PHONE_NUMBER', 33, 45, 0.75)]])]

    engine = BatchAnonymizerEngine()
    anonymized_results = engine.anonymize_dict(analyzer_results)
    assert anonymized_results == {'name': ['<PERSON>', '<PERSON>', '<PERSON>'],
        'comments': ['called him <DATE_TIME> to confirm he requested to call back in '
        '<DATE_TIME>',
        'accepted the offer license number <US_DRIVER_LICENSE>',
        'need to call him at phone number <PHONE_NUMBER>']}


def test_given_custom_anonymizer_we_anonymize_dict_correctly():
    anonymizer_config = OperatorConfig("custom", {"lambda": lambda x: f"<ENTITY: {x}>"})

    engine = BatchAnonymizerEngine()
    anonymized_results = engine.anonymize_dict(
      analyzer_results, operators={"DEFAULT": anonymizer_config})
    assert anonymized_results == {'name':
                                ['<ENTITY: John>', '<ENTITY: Jill>', '<ENTITY: Jack>']}
