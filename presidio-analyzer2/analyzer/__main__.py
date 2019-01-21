import logging
import import_models
#import matcher
import importlib
import grpc
import analyze_pb2
import analyze_pb2_grpc
from concurrent import futures
from field_types import field_factory
from abstract_recognizer import AbstractRecognizer
import time
import sys
import os
from google.protobuf.json_format import MessageToJson
from knack import CLI
from knack.arguments import ArgumentsContext
from knack.commands import CLICommandsLoader, CommandGroup
from knack.help import CLIHelp
from knack.help_files import helps
from models import regex_recognizer
#from models.regex import regex_recognizer

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

cli_name = "presidio-analyzer"

helps['serve'] = """
    short-summary: Create a GRPC server
                   - presidio-analyzer serve --grpc_port 3000
"""

helps['analyze'] = """
    short-summary: Analyze text for PII
                   - presidio-analyzer analyze --text "John Smith drivers
                   license is AC432223" --fields "PERSON" "US_DRIVER_LICENSE"
"""

loglevel = os.environ.get("LOG_LEVEL", "INFO")
logging.basicConfig(
    format='%(asctime)s:%(levelname)s:%(message)s', level=loglevel)


class PresidioCLIHelp(CLIHelp):
    def __init__(self, cli_ctx=None):
        super(PresidioCLIHelp, self).__init__(
            cli_ctx=cli_ctx,
            privacy_statement='',
            welcome_message=WELCOME_MESSAGE)


class Analyzer(analyze_pb2_grpc.AnalyzeServiceServicer):
    def __init__(self):
        # load all models
        SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
        plugins_directory_path = os.path.join(SCRIPT_DIR, 'models')
        
        self.plugins = import_models.import_plugins(
            plugins_directory_path, base_class=AbstractRecognizer)

        for plugin in self.plugins:
            logging.info(plugin)
            plugin.load_model()

    def __get_field_types(self, requested_fields):
        """ If the requested field types array is empty,
            All the supported field types will be analyzed.
        """
        field_type_string_filters = []

        if requested_fields is None or not requested_fields:
            field_type_string_filters = field_factory.types_refs
        else:
            for field_type in requested_fields:
                field_type_string_filters.append(field_type.name)

        return field_type_string_filters

    def Apply(self, request, context):
        logging.info("Starting Apply " + request.text)
        
        response = analyze_pb2.AnalyzeResponse()
        fields = self.__get_field_types(request.analyzeTemplate.fields)

        results = []

        for plugin in self.plugins:
            r = plugin.analyze_text(request.text, fields)
            if r is not None:
                results.extend(r)

        response.analyzeResults.extend(results)
        return response

def serve_command_handler(env_grpc_port=False, grpc_port=3001):

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    analyze_pb2_grpc.add_AnalyzeServiceServicer_to_server(Analyzer(), server)

    if env_grpc_port:
        port = os.environ.get('GRPC_PORT')
        if port is not None or port is not '':
            grpc_port = int(port)

    server.add_insecure_port('[::]:' + str(grpc_port))
    logging.info("Starting GRPC listener at port " + str(grpc_port))
    server.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop(0)


def analyze_command_handler(text, fields, env_grpc_port=False, grpc_port=3001):

    if env_grpc_port:
        port = os.environ.get('GRPC_PORT')
        if port is not None or port is not '':
            grpc_port = int(port)

    channel = grpc.insecure_channel('localhost:' + str(grpc_port))
    stub = analyze_pb2_grpc.AnalyzeServiceStub(channel)
    request = analyze_pb2.AnalyzeRequest()
    request.text = text

    for field_name in fields:
        field_type = request.analyzeTemplate.fields.add()
        field_type.name = field_name
    results = stub.Apply(request)
    print(MessageToJson(results))


class CommandsLoader(CLICommandsLoader):
    def load_command_table(self, args):
        with CommandGroup(self, '', '__main__#{}') as g:
            g.command('serve', 'serve_command_handler', confirmation=False),
            g.command('analyze', 'analyze_command_handler', confirmation=False)
        return super(CommandsLoader, self).load_command_table(args)

    def load_arguments(self, command):
        with ArgumentsContext(self, 'serve') as ac:
            ac.argument('env_grpc_port', default=False, required=False)
            ac.argument('grpc_port', default=3001, type=int, required=False)
        with ArgumentsContext(self, 'analyze') as ac:
            ac.argument('env_grpc_port', default=False, required=False)
            ac.argument('grpc_port', default=3001, type=int, required=False)
            ac.argument('text', required=True)
            ac.argument('fields', nargs='*', required=True)
        super(CommandsLoader, self).load_arguments(command)


presidio_cli = CLI(
    cli_name=cli_name,
    config_dir=os.path.join('~', '.{}'.format(cli_name)),
    config_env_var_prefix=cli_name,
    commands_loader_cls=CommandsLoader,
    help_cls=PresidioCLIHelp)
exit_code = presidio_cli.invoke(sys.argv[1:])
sys.exit(exit_code)
