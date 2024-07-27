# Copyright (c) 2024 AJ Welch <awelch0100@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""Dev commands."""
import nox


@nox.session(tags=["analyze"], python=False)
def format(session):  # pylint: disable=redefined-builtin
    """Execute formatters."""
    session.run("poetry", "install")
    session.run(
        "addlicense",
        "-l",
        "mit",
        "-c",
        "AJ Welch <awelch0100@gmail.com>",
        "infrastructure.py",
        "noxfile.py",
    )
    session.run(
        "poetry",
        "run",
        "black",
        "infrastructure.py",
        "noxfile.py",
    )
    session.run(
        "poetry",
        "run",
        "nbqa",
        "black",
        "glaredb_demo.ipynb",
    )
    session.run("poetry", "run", "isort", "infrastructure.py", "noxfile.py")
    session.run(
        "poetry", "run", "nbqa", "isort", "glaredb_demo.ipynb", "--float-to-top"
    )


@nox.session(tags=["analyze"], python=False)
def lint(session):
    """Execute linters."""
    session.run("poetry", "install")
    session.run("poetry", "run", "pylint", "infrastructure.py", "noxfile.py")
    session.run("npm", "install")
    session.run("npm", "exec", "markdownlint-cli2", "*.md")


@nox.session(tags=["analyze"], python=False)
def type_check(session):
    """Execute mypy."""
    session.run("poetry", "install")
    session.run("poetry", "run", "mypy", "--strict", "infrastructure.py")
