from argparse import ArgumentParser
import importlib
import os


def main():
    parser = ArgumentParser()
    add_parsers(parser)

    args = parser.parse_args()
    args.command(args)


def add_parsers(parser):
    base_dir = os.path.dirname(__file__)
    sub_parsers = parser.add_subparsers()
    for name in os.listdir(base_dir):
        root, ext = os.path.splitext(name)
        if root == '__init__' or ext != '.py':
            continue
        module = importlib.import_module('.'.join((
            'ariblib', 'command', root)))
        try:
            getattr(module, 'add_parser')(sub_parsers)
        except AttributeError:
            pass
