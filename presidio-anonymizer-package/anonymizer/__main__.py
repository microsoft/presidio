import os
from os import sys
import logging

from knack import CLI
from knack.arguments import ArgumentsContext
from knack.commands import CLICommandsLoader, CommandGroup
from knack.help import CLIHelp
from knack.help_files import helps

from analyzer.analyzer_engine import AnalyzerEngine
from anonymizer import Anonymizer


WELCOME_MESSAGE = "Welcome to PII-Obfuscator"

# define the url domain for pii-obfuscation project
CLI_NAME = "pii-obfuscator"

# define help docs
helps['text'] = """
    short-summary: Obfuscate a single piece of text\n
                   - pii-obfuscator text --text "John Smith drivers license is AC432223"
                """
helps['directory'] = """
    short-summary: Obfuscator text files under input directory and store to output directory\n
                   - pii-obfuscator directory 
                        --input-path <raw files folder> 
                        --output-path <obfuscated files folder>
                    """

# setting logging info
loglevel = os.environ.get("LOG_LEVEL", "INFO")
logging.basicConfig(
    format='%(asctime)s:%(levelname)s:%(message)s', level=loglevel)


class PresidioCLIHelp(CLIHelp):
    def __init__(self, cli_ctx=None):
        super(PresidioCLIHelp, self).__init__(
            cli_ctx=cli_ctx,
            privacy_statement='',
            welcome_message=WELCOME_MESSAGE)


# handle the case which takes text as argument
def text_command_handler(text, fields,domain_name):

    if not domain_name:
        domain_name = 'DEFAULT_DOMAIN'

    # initialize an analyzer engine
    analyzer = AnalyzerEngine()
    anonymizer = Anonymizer(0.5)

    # if no fields or empty fields passed, set the indicator all_fields to false
    all_fields = False
    if fields == [] or fields is None:
        all_fields = True

    # get result from analyzer engine
    results = analyzer.analyze("id",text, fields, "en", all_fields)
    print(anonymizer.anonymize(text, results,domain_name))


# handle the case which takes files as argument
def directory_command_handler(input_path, output_path, fields,domain_name):

    if not domain_name:
        domain_name = 'DEFAULT_DOMAIN'

    # initialize an analyzer engine
    analyzer = AnalyzerEngine()
    anonymizer = Anonymizer(0.5)

    # if no fields or empty fields passed, set the indicator all_fields to false
    all_fields = False
    if fields == [] or fields is None:
        all_fields = True

    # execute the anonymize process on each file in the given file path
    for filename in os.listdir(input_path):
        if filename[0] == ".":
            pass
        else:
            if input_path[-1] == "/":
                input_path = input_path[:-1]
            if output_path[-1] == "/":
                output_path = output_path[:-1]
            f = open(input_path + "/" + filename, 'r')
            text = f.read()
            f.close()

            # get result from analyzer engine
            results = analyzer.analyze(
                correlation_id="id",
                text=text,
                entities=fields,
                language='en',
                all_fields=all_fields
            )
            obfuscated_text = anonymizer.anonymize(text, results,domain_name)
            obfuscated_file = open(output_path + "/" + filename, "w")
            obfuscated_file.write(obfuscated_text)
            obfuscated_file.close()


# set the class for loading commands
class CommandsLoader(CLICommandsLoader):

    def load_command_table(self, args):
        with CommandGroup(self, '', '__main__#{}') as g:
            g.command('text', 'text_command_handler', confirmation=False)
            g.command('directory', 'directory_command_handler', confirmation=False)
        return super(CommandsLoader, self).load_command_table(args)

    def load_arguments(self, command):
        with ArgumentsContext(self, 'text') as ac:
            ac.argument('text', required=True)
            ac.argument('fields', nargs='*', required=False)
            ac.argument('domain_name', required=False)
        with ArgumentsContext(self, 'directory') as ac:
            ac.argument('input_path', required=True)
            ac.argument('output_path', required=True)
            ac.argument('fields', nargs='*', required=False)
            ac.argument('domain_name', required=False)
        super(CommandsLoader, self).load_arguments(command)


# define the command line interface using the classed defined above
presidio_cli = CLI(
    cli_name=CLI_NAME,
    config_dir=os.path.join('~', ('.' + CLI_NAME)),
    config_env_var_prefix=CLI_NAME,
    commands_loader_cls=CommandsLoader,
    help_cls=PresidioCLIHelp)
exit_code = presidio_cli.invoke(sys.argv[1:])
sys.exit(exit_code)
