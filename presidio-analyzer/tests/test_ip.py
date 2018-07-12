from analyzer import matcher
from analyzer import common_pb2
import logging
import os


fieldType = common_pb2.FieldTypes()
fieldType.name = common_pb2.FieldTypesEnum.Name(common_pb2.IP_ADDRESS)
types = [fieldType]


def test_valid_ipv4():
    match = matcher.Matcher()
    ip = 'microsoft.com 192.168.0.1'
    results = match.analyze_text('the ip is ' + ip, types)
    assert len(results) == 1


def test_invalid_ipv4():
    match = matcher.Matcher()
    ip = '192.168.0'
    results = match.analyze_text('the ip is ' + ip, types)
    assert len(results) == 0
