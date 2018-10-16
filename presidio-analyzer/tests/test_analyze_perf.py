from analyzer import matcher, common_pb2
from tests import *
import datetime
import os

context = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean commodo dictum est, fringilla congue ex malesuada quis. Phasellus at posuere erat. Quisque blandit tristique lacus ut aliquam. Donec at maximus nisi. Quisque dapibus eros enim, quis tincidunt leo vehicula at. Maecenas suscipit nec ante pretium ornare. Nulla at dui vel mi blandit scelerisque. Phasellus vehicula vel nunc et convallis. Pellentesque nibh elit, molestie a lectus vitae, luctus fringilla quam. '

PERF_MICROSECS_THRESHOLD_ENTITY = 300000
PERF_MICROSECS_THRESHOLD_CHECKSUM_ENTITY = 350000
PERF_MICROSECS_THRESHOLD_NER = 200000

def analyze_perf(field_name, entity, runtime_threshold_micros):
    fieldType = common_pb2.FieldTypes()
    fieldType.name = field_name
    types = [fieldType]

    start_time = datetime.datetime.now()
    results = match.analyze_text(context + entity, types)
    analyze_time = datetime.datetime.now() - start_time

    print('--- analyze_time[{}]: {}.{} seconds'.format(
            types[0].name, analyze_time.seconds, analyze_time.microseconds))
    
    assert analyze_time.seconds < 1
    assert analyze_time.microseconds < runtime_threshold_micros

# Credit Card
def test_analyze_perf_credit_card_no_dashes():
    field_name = common_pb2.FieldTypesEnum.Name(common_pb2.CREDIT_CARD)
    entity = '4012888888881881'
    analyze_perf(field_name, entity, PERF_MICROSECS_THRESHOLD_CHECKSUM_ENTITY)
    

def test_analyze_perf_credit_card_with_dashes():
    field_name = common_pb2.FieldTypesEnum.Name(common_pb2.CREDIT_CARD)
    entity = '4012-8888-8888-1881'
    analyze_perf(field_name, entity, PERF_MICROSECS_THRESHOLD_CHECKSUM_ENTITY)


def test_analyze_perf_credit_card_diners_no_dashes():
    field_name = common_pb2.FieldTypesEnum.Name(common_pb2.CREDIT_CARD)
    entity = '30569309025904'
    analyze_perf(field_name, entity, PERF_MICROSECS_THRESHOLD_CHECKSUM_ENTITY)


# Crypto
def test_analyze_perf_btc():
    field_name = common_pb2.FieldTypesEnum.Name(common_pb2.CREDIT_CARD)
    entity = '16Yeky6GMjeNkAiNcBY7ZhrLoMSgg1BoyZ'
    analyze_perf(field_name, entity, PERF_MICROSECS_THRESHOLD_CHECKSUM_ENTITY)

# Domain
def test_analyze_perf_domain():
    field_name = common_pb2.FieldTypesEnum.Name(common_pb2.DOMAIN_NAME)
    entity = 'microsoft.com'
    analyze_perf(field_name, entity, PERF_MICROSECS_THRESHOLD_CHECKSUM_ENTITY)

# Email
def test_analyze_perf_email():
    field_name = common_pb2.FieldTypesEnum.Name(common_pb2.EMAIL_ADDRESS)
    entity = 'info@presidio.site'
    analyze_perf(field_name, entity, PERF_MICROSECS_THRESHOLD_CHECKSUM_ENTITY)

# IBAN
def test_analyze_perf_iban():
    field_name = common_pb2.FieldTypesEnum.Name(common_pb2.IBAN_CODE)
    entity = 'IL150120690000003111111'
    analyze_perf(field_name, entity, PERF_MICROSECS_THRESHOLD_CHECKSUM_ENTITY)

# IP
def test_analyze_perf_ipv4():
    field_name = common_pb2.FieldTypesEnum.Name(common_pb2.IP_ADDRESS)
    entity = '192.168.0.1'
    analyze_perf(field_name, entity, PERF_MICROSECS_THRESHOLD_ENTITY)

# NER
def test_analyze_perf_person():
    field_name = common_pb2.FieldTypesEnum.Name(common_pb2.PERSON)
    entity = 'John Oliver'
    analyze_perf(field_name, entity, PERF_MICROSECS_THRESHOLD_NER)


def test_analyze_perf_person():
    field_name = common_pb2.FieldTypesEnum.Name(common_pb2.DATE_TIME)
    entity = 'May 1st'
    analyze_perf(field_name, entity, PERF_MICROSECS_THRESHOLD_NER)

# US - Bank Account
def test_analyze_perf_us_bank():
    field_name = common_pb2.FieldTypesEnum.Name(common_pb2.US_BANK_NUMBER)
    entity = '945456787654'
    analyze_perf(field_name, entity, PERF_MICROSECS_THRESHOLD_ENTITY)

# US - Driver License
def test_analyze_perf_us_driver_license_very_weak_digits():
    field_name = common_pb2.FieldTypesEnum.Name(common_pb2.US_DRIVER_LICENSE)
    entity = '123456789'
    analyze_perf(field_name, entity, PERF_MICROSECS_THRESHOLD_ENTITY)


def test_analyze_perf_us_driver_license_very_weak_letters():
    field_name = common_pb2.FieldTypesEnum.Name(common_pb2.US_DRIVER_LICENSE)
    entity = 'ABCDEFGHI'
    analyze_perf(field_name, entity, PERF_MICROSECS_THRESHOLD_ENTITY)


# US - Itin
def test_analyze_perf_us_itin():
    field_name = common_pb2.FieldTypesEnum.Name(common_pb2.US_ITIN)
    entity = '911-701234'
    analyze_perf(field_name, entity, PERF_MICROSECS_THRESHOLD_ENTITY)


# US - Passport
def test_analyze_perf_us_passport():
    field_name = common_pb2.FieldTypesEnum.Name(common_pb2.US_PASSPORT)
    entity = '912803456'
    analyze_perf(field_name, entity, PERF_MICROSECS_THRESHOLD_ENTITY)


# US - Phone
def test_analyze_perf_phone():
    field_name = common_pb2.FieldTypesEnum.Name(common_pb2.PHONE_NUMBER)
    entity = '(425) 882-9090'
    analyze_perf(field_name, entity, PERF_MICROSECS_THRESHOLD_ENTITY)


# US - SSN
def test_analyze_perf_us_ssn():
    field_name = common_pb2.FieldTypesEnum.Name(common_pb2.US_SSN)
    entity = '078-05-1120'
    analyze_perf(field_name, entity, PERF_MICROSECS_THRESHOLD_ENTITY)