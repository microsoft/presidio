import logging
import matcher
import grpc
import analyze_pb2
import analyze_pb2_grpc
import common_pb2
import template_pb2
from concurrent import futures
import time
import sys
import os


class Analyzer(analyze_pb2_grpc.AnalyzeServiceServicer):
    def __init__(self):
        self.match = matcher.Matcher()

    def Apply(self, request, context):
        response = analyze_pb2.AnalyzeResponse()
        results = self.match.analyze_text(
            request.text, request.analyzeTemplate.fields)
        response.analyzeResults.extend(results)
        return response


def serve():

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    analyze_pb2_grpc.add_AnalyzeServiceServicer_to_server(Analyzer(), server)

    port = os.environ['GRPC_PORT']
    if port is None or port == '':
        port = 3001

    server.add_insecure_port('[::]:' + str(port))
    logging.info("Starting GRPC listener at port " + port)
    server.start()
    try:
        while True:
            time.sleep(0)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()
