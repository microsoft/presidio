import os

import grpc
from presidio_analyzer.protobuf_models import (
    recognizers_store_pb2,
    recognizers_store_pb2_grpc,
)

from presidio_analyzer import PatternRecognizer, Pattern, PresidioLogger


logger = PresidioLogger("presidio")


class RecognizerStoreApi:
    """ The RecognizerStoreApi is the object that talks to the remote
    recognizers store service and get the recognizers / hash
    """

    def __init__(self):
        try:
            recognizers_store_svc_url = \
                os.environ["RECOGNIZERS_STORE_SVC_ADDRESS"]
        except KeyError:
            recognizers_store_svc_url = "localhost:3004"

        channel = grpc.insecure_channel(recognizers_store_svc_url)
        self.rs_stub = recognizers_store_pb2_grpc.RecognizersStoreServiceStub(
            channel)

    def get_latest_hash(self):
        """
        Returns the hash of all the stored custom recognizers. Returns empty
        string in case of an error (e.g. the store is completly empty)
        """

        hash_request = \
            recognizers_store_pb2.RecognizerGetHashRequest()

        last_hash = ""
        try:
            # todo: task 812: Change to pub sub pattern
            last_hash = self.rs_stub.ApplyGetHash(
                hash_request).recognizersHash
        except grpc.RpcError:
            logger.error("Failed to get recognizers hash")
            return None

        if not last_hash:
            logger.info("Recognizers hash was not found in store")
        else:
            logger.info("Latest hash found in store is: %s", str(last_hash))
        return last_hash

    def get_all_recognizers(self):
        """
        Returns a list of CustomRecognizer which were created from the
        recognizers stored in the underlying store
        """
        req = recognizers_store_pb2.RecognizersGetAllRequest()
        raw_recognizers = []

        try:
            raw_recognizers = self.rs_stub.ApplyGetAll(req).recognizers

        except grpc.RpcError:
            logger.info("Failed getting recognizers from the remote store. \
            Returning an empty list")
            return raw_recognizers

        custom_recognizers = []
        for new_recognizer in raw_recognizers:
            patterns = []
            for pat in new_recognizer.patterns:
                patterns.extend(
                    [Pattern(pat.name, pat.regex, pat.score)])
            new_custom_recognizer = PatternRecognizer(
                name=new_recognizer.name,
                supported_entity=new_recognizer.entity,
                supported_language=new_recognizer.language,
                black_list=new_recognizer.blacklist,
                context=new_recognizer.contextPhrases,
                patterns=patterns)
            custom_recognizers.append(
                new_custom_recognizer)

        return custom_recognizers
