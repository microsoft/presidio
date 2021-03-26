(my_env) newwen@newwen-ECQ3-0:~/presidio/presidio-image-redactor$ pipenv run pytest
============================= test session starts ==============================
platform linux -- Python 3.9.2, pytest-6.2.2, py-1.10.0, pluggy-0.13.1
rootdir: /home/newwen/presidio/presidio-image-redactor
plugins: anyio-2.2.0
collected 27 items                                                             

tests/test_api_request_convertor.py ...........                          [ 40%]
tests/test_image_analyzer_engine.py .......                              [ 66%]
tests/test_ocr.py ....                                                   [ 81%]
tests/integration/test_image_analyzer_engine_integration.py ..           [ 88%]
tests/integration/test_image_redactor_engine.py ...                      [100%]

(presidio-e2e) (base) newwen@newwen-ECQ3-0:~/presidio/e2e-tests$ pytest
============================= test session starts ==============================
platform linux -- Python 3.8.5, pytest-6.2.2, py-1.10.0, pluggy-0.13.1
rootdir: /home/newwen/presidio/e2e-tests, configfile: pytest.ini
collected 34 items                                                             

tests/test_analyzer.py ...............                                   [ 44%]
tests/test_anonymizer.py ...........                                     [ 76%]
tests/test_e2e_integration_flows.py ......                               [ 94%]
tests/test_image_redactor.py ..                                          [100%]
