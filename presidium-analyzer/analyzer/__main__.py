import logging
import matcher
import grpc
import analyze_pb2
import analyze_pb2_grpc
from concurrent import futures
import time

_UNLIMITED_TIME = 60 * 60 * 2400


class Analyzer(analyze_pb2_grpc.AnalyzeServiceServicer):

    def __init__(self,):
        self.match = matcher.Matcher()

    def Apply(self, request, context):
        results = analyze_pb2.Results()
        results.results.extend(self.match.analyze_text(
            request.value, request.fields))
        return results


def serve():

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    analyze_pb2_grpc.add_AnalyzeServiceServicer_to_server(Analyzer(), server)
    server.add_insecure_port('[::]:3001')
    server.start()
    try:
        while True:
            time.sleep(_UNLIMITED_TIME)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()
