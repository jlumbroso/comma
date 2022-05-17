import os
import re

import comma


VERSION_NUMBER = "0.5.4"
POETRY_FILE = "pyproject.toml"


def get_pyproject_version() -> str:
    """
    Returns the version number contained in the Poetry package
    definition file.
    """
    comma_init_filepath = comma.__file__
    comma_root_dir = os.path.abspath(
        os.path.join(os.path.dirname(comma_init_filepath), ".."))

    pyproject_path = os.path.join(comma_root_dir, POETRY_FILE)

    assert os.path.exists(pyproject_path), "check poetry file exists"

    try:
        pyproject_src = open(pyproject_path).read()
    except UnicodeDecodeError:
        pyproject_src = open(
            pyproject_path, "rb").read().decode(encoding="utf-8")
    version_match = re.search(
        r"version\s*=\s*\"([^\"]*)\"",
        pyproject_src)

    assert version_match, "check poetry file version info can be parsed"
    return version_match.group(1)


def test_package_version():
    assert comma.__version__ == VERSION_NUMBER, "check version in comma/__init__.py"


def test_pyproject_version():
    assert get_pyproject_version() == VERSION_NUMBER, "check version in pyproject.toml"


def test_consistent_version():
    assert comma.__version__ == get_pyproject_version(), "check version consistency"
