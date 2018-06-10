import logging
import matcher
import grpc
from protocol import analyze_pb2
from protocol import analyze_pb2_grpc
from concurrent import futures
import time
import sys


class Analyzer(analyze_pb2_grpc.AnalyzeServiceServicer):
    def __init__(self, ):
        self.match = matcher.Matcher()

    def Apply(self, request, context):
        results = analyze_pb2.Results()
        results.results.extend(
            self.match.analyze_text(request.value, request.fields))
        return results


def serve():

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    analyze_pb2_grpc.add_AnalyzeServiceServicer_to_server(Analyzer(), server)

    port = os.environ['GRPC_PORT']
    if port is None or port == '':
        port = 3001

    server.add_insecure_port('[::]:' + str(port))
    server.start()
    try:
        while True:
            time.sleep(sys.maxint)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()
