import argparse
import os
import sys
import io
import locale
import platform
import json


from presidio_cli import SHELL_NAME, APP_DESCRIPTION, APP_VERSION
from presidio_cli.analyzer import analyze
from presidio_cli.config import PresidioCLIConfig, PresidioCLIConfigError


class Format(object):
    @staticmethod
    def parsable(problem):
        return json.dumps(problem.recognizer_result)

    @staticmethod
    def standard(problem):
        line = "  %d:%d" % (problem.line, problem.column)
        line += max(12 - len(line), 0) * " "
        line += str(problem.score)
        line += max(21 - len(line), 0) * " "
        line += problem.type
        if problem.explanation:
            line += "  (%s)" % problem.explanation
        return line

    @staticmethod
    def standard_color(problem):
        line = "  \033[2m%d:%d\033[0m" % (problem.line, problem.column)
        line += max(20 - len(line), 0) * " "
        if problem.score < 1:  # warning
            line += "\033[33m%s\033[0m" % problem.score
        else:
            line += "\033[31m%s\033[0m" % problem.score
        line += max(38 - len(line), 0) * " "
        line += problem.type
        if problem.explanation:
            line += "  \033[2m(%s)\033[0m" % problem.explanation
        return line

    @staticmethod
    def github(problem, filename):
        line = "::"
        line += str(problem.score)
        line += " file=" + filename + ","
        line += "line=" + format(problem.line) + ","
        line += "col=" + format(problem.column)
        line += "::"
        line += format(problem.line)
        line += ":"
        line += format(problem.column)
        line += " "
        line += "[" + problem.type + "] "
        if problem.explanation:
            line += problem.explanation
        return line


def supports_color():
    supported_platform = not (
        platform.system() == "Windows"
        and not (
            "ANSICON" in os.environ
            or ("TERM" in os.environ and os.environ["TERM"] == "ANSI")
        )
    )
    return supported_platform and hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def show_problems(problems, file, args_format, no_warn):
    max_level = 0
    first = True

    if args_format == "auto":
        if "GITHUB_ACTIONS" in os.environ and "GITHUB_WORKFLOW" in os.environ:
            args_format = "github"
        elif supports_color():
            args_format = "colored"

    for problem in problems:
        if no_warn and (problem.level != "error"):
            continue
        if args_format == "parsable":
            print(Format.parsable(problem))
        elif args_format == "github":
            if first:
                print("::group::%s" % file)
                first = False
            print(Format.github(problem, file))
        elif args_format == "colored":
            if first:
                print("\033[4m%s\033[0m" % file)
                first = False
            print(Format.standard_color(problem))
        else:
            if first:
                print(file)
                first = False
            print(Format.standard(problem))
        # max_level+=1

    if not first and args_format == "github":
        print("::endgroup::")

    if not first and args_format != "parsable":
        print("")

    return max_level


def find_files_recursively(items, conf):
    for item in items:
        if os.path.isdir(item):
            for root, dirnames, filenames in os.walk(item):
                for f in filenames:
                    filepath = os.path.join(root, f)
                    if conf.is_text_file(filepath):
                        yield filepath
        else:
            if conf.is_text_file(item):
                yield item


def run():
    parser = argparse.ArgumentParser(prog=SHELL_NAME, description=APP_DESCRIPTION)

    parser.add_argument("-v", "--version", action="version", version=f"v{APP_VERSION}")

    files_group = parser.add_mutually_exclusive_group(required=True)
    files_group.add_argument(
        "files",
        metavar="FILE_OR_DIR",
        nargs="*",
        default=(),
        help="files to check",
    )
    files_group.add_argument(
        "-", action="store_true", dest="stdin", help="read from standard input"
    )

    config_group = parser.add_mutually_exclusive_group()
    config_group.add_argument(
        "-c",
        "--config-file",
        dest="config_file",
        action="store",
        help="path to a custom configuration",
    )

    config_group.add_argument(
        "-d",
        "--config-data",
        dest="config_data",
        action="store",
        help="custom configuration (as YAML source)",
    )

    parser.add_argument(
        "-f",
        "--format",
        choices=("standard", "github", "auto", "colored", "parsable"),
        default="auto",
        help="format for parsing output",
    )

    parser.add_argument(
        "--no-warnings",
        action="store_true",
        help="output only error level problems",
    )

    args = parser.parse_args()

    try:
        if args.config_data is not None:
            if args.config_data != "" and ":" not in args.config_data:
                args.config_data = "extends: " + args.config_data
            conf = PresidioCLIConfig(content=args.config_data)
        elif args.config_file is not None:
            conf = PresidioCLIConfig(file=args.config_file)
        elif os.path.isfile(".presidiocli"):
            conf = PresidioCLIConfig(file=".presidiocli")
        else:
            conf = PresidioCLIConfig(content="extends: default")
    except PresidioCLIConfigError as e:
        print(e, file=sys.stderr)
        sys.exit(1)

    if conf.locale is not None:
        locale.setlocale(locale.LC_ALL, conf.locale)

    prob_num = 0
    for file in find_files_recursively(args.files, conf):
        filepath = file[2:] if file.startswith("./") else file
        try:
            with io.open(file, newline="") as f:
                problems = analyze(f, conf, filepath)
        except EnvironmentError as e:
            print(e, file=sys.stderr)
            sys.exit(1)
        prob_num = show_problems(
            problems, file, args_format=args.format, no_warn=args.no_warnings
        )

    if args.stdin:
        try:
            problems = analyze(sys.stdin, conf, "")
        except EnvironmentError as e:
            print(e, file=sys.stderr)
            sys.exit(1)
        prob_num = show_problems(
            problems,
            "stdin",
            args_format=args.format,
            no_warn=args.no_warnings,
        )

    if prob_num > 0:
        return_code = 1
    else:
        return_code = 0
    sys.exit(return_code)
