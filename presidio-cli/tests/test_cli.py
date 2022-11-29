import os
import pytest
from io import StringIO
from presidio_cli import cli


@pytest.fixture()
def problems(mocker):
    problem1 = mocker.Mock(
        line=1,
        column=7,
        score=1.0,
        type="PERSON",
        explanation=None,
        recognizer_result={},
    )
    problem2 = mocker.Mock(
        line=2,
        column=17,
        score=0.85,
        type="PERSON",
        explanation="some example",
        recognizer_result={},
    )
    return [problem1, problem2]


def test_find_files_recursively(temp_workspace, config):
    assert sorted(cli.find_files_recursively([temp_workspace], config)) == [
        os.path.join(temp_workspace, "dos.yml"),
        os.path.join(temp_workspace, "empty.txt"),
        os.path.join(temp_workspace, "errorfile"),
        os.path.join(temp_workspace, "non-ascii", "éçäγλνπ¥", "utf-8"),
        os.path.join(temp_workspace, *["s"] * 15, "file"),
        os.path.join(temp_workspace, "sub", "directory.txt", "empty.txt"),
    ]


@pytest.mark.parametrize(
    "arg_format",
    [
        "auto",
        "standard",
        "colored",
        "github",
        "parsable",
    ],
)
def test_show_problems(arg_format, problems):
    filepath = "./example.txt"

    rc = cli.show_problems(problems, filepath, arg_format, False)
    assert rc == 0


def test_show_problems_auto_gh(problems, monkeypatch):
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("GITHUB_WORKFLOW", "true")

    filepath = "./example.txt"
    rc = cli.show_problems(problems, filepath, "auto", False)
    assert rc == 0


def test_show_problems_auto_color(problems, monkeypatch, mocker):
    monkeypatch.setenv("TERM", "xterm-256color")
    mocker.patch("sys.stdout")
    filepath = "./example.txt"
    rc = cli.show_problems(problems, filepath, "auto", False)
    assert rc == 0


def test_run_current_dir(temp_workspace, mocker):
    os.chdir(temp_workspace)
    mocker.patch("sys.argv", ["", "."])
    ec = mocker.patch("sys.exit")
    cli.run()
    ec.assert_called_once_with(0)


def test_run_with_config(temp_workspace, mocker):

    with open(os.path.join(temp_workspace, ".presidiocli"), "w") as f:
        f.write("extends: default\n")

    os.chdir(temp_workspace)
    mocker.patch("sys.argv", ["-c", ".presidiocli", "."])
    ec = mocker.patch("sys.exit")
    cli.run()
    ec.assert_called_once_with(0)


def test_run_with_stdin(mocker):
    mocked_args = mocker.Mock(stdin=True, config_data=None, config_file=None, files="")
    ec = mocker.patch("sys.exit")
    with mocker.patch("argparse.ArgumentParser.parse_args", return_value=mocked_args):
        with mocker.patch("sys.stdin", StringIO("Example input")):
            cli.run()
    ec.assert_called_once_with(0)
