# pylint: disable=wrong-import-position,wrong-import-order
import logging
from concurrent import futures
import os
import time
import sys

import grpc
from google.protobuf.json_format import MessageToJson
from knack import CLI
from knack.arguments import ArgumentsContext
from knack.commands import CLICommandsLoader, CommandGroup
from knack.help import CLIHelp
from knack.help_files import helps

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from presidio_analyzer.protobuf_models import analyze_pb2, analyze_pb2_grpc # noqa
from presidio_analyzer import AnalyzerEngine, PresidioLogger, RecognizerRegistry # noqa
from presidio_analyzer.nlp_engine import SpacyNlpEngine # noqa

log_level_name = os.environ.get('LOG_LEVEL', 'INFO')
log_level = logging.INFO
if log_level_name == 'WARNING':
    log_level = logging.WARNING
if log_level_name == 'ERROR':
    log_level = logging.ERROR
logger = PresidioLogger("presidio")
logger.set_level(log_level)

WELCOME_MESSAGE = r"""

 _______  _______  _______  _______ _________ ______  _________ _______
(  ____ )(  ____ )(  ____ \(  ____ \\__   __/(  __  \ \__   __/(  ___  )
| (    )|| (    )|| (    \/| (    \/   ) (   | (  \  )   ) (   | (   ) |
| (____)|| (____)|| (__    | (_____    | |   | |   ) |   | |   | |   | |
|  _____)|     __)|  __)   (_____  )   | |   | |   | |   | |   | |   | |
| (      | (\ (   | (            ) |   | |   | |   ) |   | |   | |   | |
| )      | ) \ \__| (____/\/\____) |___) (___| (__/  )___) (___| (___) |
|/       |/   \__/(_______/\_______)\_______/(______/ \_______/(_______)

"""

CLI_NAME = "presidio-analyzer"

helps['serve'] = """
    short-summary: Create a GRPC server
                   - presidio-analyzer serve --grpc-port 3000
"""

helps['analyze'] = """
    short-summary: Analyze text for PII
                   - presidio-analyzer analyze --text "John Smith drivers
                   license is AC432223" --fields "PERSON" "US_DRIVER_LICENSE"
"""


class PresidioCLIHelp(CLIHelp):
    def __init__(self, cli_ctx=None):
        super(PresidioCLIHelp, self).__init__(
            cli_ctx=cli_ctx,
            privacy_statement='',
            welcome_message=WELCOME_MESSAGE)


def serve_command_handler(enable_trace_pii,
                          env_grpc_port=False,
                          grpc_port=3000):
    logger.info("Starting GRPC server")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    logger.info("GRPC started")

    logger.info("Creating RecognizerRegistry")
    registry = RecognizerRegistry()
    logger.info("RecognizerRegistry created")
    logger.info("Creating SpacyNlpEngine")
    nlp_engine = SpacyNlpEngine()
    logger.info("SpacyNlpEngine created")

    analyze_pb2_grpc.add_AnalyzeServiceServicer_to_server(
        AnalyzerEngine(registry=registry,
                       nlp_engine=nlp_engine,
                       enable_trace_pii=enable_trace_pii,
                       use_recognizer_store=True),
        server)

    logger.info("Added AnalyzeServiceServicer to server")

    if env_grpc_port:
        logger.info("Getting port {}".format(env_grpc_port))
        port = os.environ.get('GRPC_PORT')
        if port is not None or port != '':
            grpc_port = int(port)
    else:
        logger.info("env_grpc_port not provided. "
                    "Using grpc_port {}".format(grpc_port))

    server.add_insecure_port('[::]:' + str(grpc_port))
    logger.info("Starting GRPC listener at port {}".format(grpc_port))
    server.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop(0)


def analyze_command_handler(text, fields, env_grpc_port=False, grpc_port=3001):

    if env_grpc_port:
        port = os.environ.get('GRPC_PORT')
        if port is not None or port != '':
            grpc_port = int(port)

    channel = grpc.insecure_channel('localhost:' + str(grpc_port))
    stub = analyze_pb2_grpc.AnalyzeServiceStub(channel)
    request = analyze_pb2.AnalyzeRequest()
    request.text = text

    # pylint: disable=no-member
    for field_name in fields:
        field_type = request.analyzeTemplate.fields.add()
        field_type.name = field_name
    results = stub.Apply(request)
    print(MessageToJson(results))


class CommandsLoader(CLICommandsLoader):
    def load_command_table(self, args):
        with CommandGroup(self, '', '__main__#{}') as g:
            g.command('serve', 'serve_command_handler', confirmation=False)
            g.command('analyze', 'analyze_command_handler', confirmation=False)
        return super(CommandsLoader, self).load_command_table(args)

    def load_arguments(self, command):
        enable_trace_pii = os.environ.get('ENABLE_TRACE_PII')
        if enable_trace_pii is None:
            enable_trace_pii = False

        with ArgumentsContext(self, 'serve') as ac:
            ac.argument('env_grpc_port', default=False, required=False)
            ac.argument('enable_trace_pii',
                        default=enable_trace_pii,
                        required=False)
            ac.argument('grpc_port', default=3001, type=int, required=False)
        with ArgumentsContext(self, 'analyze') as ac:
            ac.argument('env_grpc_port', default=False, required=False)
            ac.argument('grpc_port', default=3001, type=int, required=False)
            ac.argument('text', required=True)
            ac.argument('fields', nargs='*', required=True)
        super(CommandsLoader, self).load_arguments(command)


presidio_cli = CLI(
    cli_name=CLI_NAME,
    config_dir=os.path.join('~', '.{}'.format(CLI_NAME)),
    config_env_var_prefix=CLI_NAME,
    commands_loader_cls=CommandsLoader,
    help_cls=PresidioCLIHelp)
exit_code = presidio_cli.invoke(sys.argv[1:])
sys.exit(exit_code)
