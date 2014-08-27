from __future__ import print_function
import argparse
from pprint import pformat

import sys
from pathlib import Path
import traceback
from easy_cheese import discover


def prompt(msg=None):
    if msg:
        sys.stderr.write(str(msg))
    return input()


def find(path, *funcs):
    for func in funcs:
        try:
            return func(path)
        except Exception:
            print('discover test failed', file=sys.stderr)
            traceback.print_exc()


def need(option, path):
    """
    Call funcs until one returns a value for ``name``, or prompt for the value.

    :param option:Option
    :return: new value or None
    """

    value = find(path, *option.functions)
    if value:
        return value

    while option.ask:
        value = prompt('{}: '.format(option.prompt))

        if value or not option.required:
            break
        print('{} is required'.format(option.name), file=sys.stderr)

    return value


class Option():
    def __init__(self, name, prompt, functions=None, required=True, multiple=False, ask=True):
        self.name = name
        self.prompt = prompt
        self.required = required
        self.functions = functions or []
        self.multiple = multiple
        self.ask = ask
        super().__init__()


SETUP_DATA = [
    Option('name', "The project name", [discover.project_name]),
    Option('version', "Version"),
    Option('author', "The project author's name", [discover.git_author_name]),
    Option('author_email', "The project author's email address", [discover.git_author_email]),
    Option('description', "Short (one line) description", required=False),
    Option('url', "Project URL"),
    Option('py_modules', "Modules not in a package", [discover.modules],
           required=False, multiple=True, ask=False),
    Option('install_requires', "Project requirements", [discover.requirements],
           required=False, multiple=True, ask=False),
]


def _main():
    parser = argparse.ArgumentParser(description='Easily generate setup.py')

    for option in SETUP_DATA:
        nargs = 1
        if option.multiple:
            nargs = '+' if option.required else '*'
        parser.add_argument('--' + option.name, help=option.prompt, nargs=nargs, required=False)

    path = Path.cwd()
    args = parser.parse_args()

    setup = {}
    # prompt for required stuff we didn't get
    for option in SETUP_DATA:
        value = getattr(args, option.name, None)
        if value is None:
            value = need(option, path)

        if value:
            setup[option.name] = value

    print('from setuptools import setup, find_packages\n\n')
    print('setup(')
    for option in SETUP_DATA:
        value = setup.get(option.name)
        if value is None:
            continue

        print('    {}='.format(option.name), end='')
        if isinstance(value, (list, dict)):
            print(pformat(value, indent=8).lstrip(), end='')
        else:
            print(repr(value), end='')
        print(',')

    print('    packages=find_packages(exclude=("tests",)),')
    print(')')


def main():
    try:
        _main()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
