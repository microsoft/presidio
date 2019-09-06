#!/usr/bin/env python
from analyzer import AnalyzerEngine

analyzer = AnalyzerEngine()
results = analyzer.analyze(text="My phone number is 212-555-5555 and my PII info fin/nric: G1277988L, sunil@datarepublic.com  ",
                           entities=[],
                           language='en',
                           all_fields=True)
print(
    ["Entity: {ent}, score: {score}\n".format(ent=res.entity_type,
                                              score=res.score)
      for res in results])