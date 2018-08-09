#!/usr/bin/env python

"""
depman - Dependency management for those who are tired of dependency management

depman is a source dependency management tool that aims to be as simple and functional as possible.

See https://github.com/Mischa-Alff/depman for more information.
"""

import os
import sys
import json
import argparse
from urllib.parse import urlparse
import logging

DEPMAN_VERSION = '0.0.0'


logging.basicConfig(
    format="%(levelname)s:%(filename)s:%(lineno)d (%(funcName)s): %(message)s",
    level=logging.INFO
)

DEPMAN_LOGGER = logging.getLogger(__name__)


class Config:
    depfile = None
    dependencies = None
    command = None
    args = None


def handle_args(argv):
    default_depfile = os.path.join(os.getcwd(), 'depman.json')
    parser = argparse.ArgumentParser(
        description="A simple, lightweight dependency management tool for those who are tired of dependency management."
    )
    parser.add_argument('--version', action='version', version='%%(prog)s %s' % DEPMAN_VERSION)
    parser.add_argument(
        '-f', '--depfile',
        dest="depfile", help="use DEPFILE as dependencies list, defaults to $cwd/depman.json",
        metavar='DEPFILE', default=default_depfile
    )

    subparsers = parser.add_subparsers(help='Commands', dest='command')
    subparsers.add_parser('list', help='Lists all dependencies from depman.json')

    args = parser.parse_args(argv)

    config = Config()
    config.depfile = args.depfile
    config.command = args.command
    config.args = args

    return config


class Dependency:
    name = None
    location = None
    version = None


def get_name_from_url(url):
    parsed = urlparse(url)
    name = parsed.hostname
    if parsed.path is not None:
        split = parsed.path.split('/')
        if split:
            name = split[-1]
            name = os.path.splitext(name)[0]
    return name


def parse_dependency(dependency):
    dep = Dependency()
    dep.name = dependency.get('name', None)
    dep.location = dependency.get('location', None)
    dep.version = dependency.get('version', None)

    if dep.location is None:
        DEPMAN_LOGGER.error('Dependency {0} has no location!'.format(dep.name))
        raise Exception

    if dep.name is None:
        dep.name = get_name_from_url(dep.location)

    if dep.version is None:
        dep.version = 'HEAD'

    return dep


def parse_deplist(deplist):
    deps = [parse_dependency(x) for x in deplist]
    return deps


def parse_depfile(config):
    if not os.path.exists(config.depfile):
        DEPMAN_LOGGER.error('Could not file depfile {0}'.format(config.depfile))
        return Config()

    with open(config.depfile, 'r') as f:
        depfile = json.load(f)
        f.close()

        deplist = depfile.get('dependencies', [])
        if not deplist:
            DEPMAN_LOGGER.warning('Depfile has no dependencies.')
        config.dependencies = parse_deplist(deplist)


def list_deps(config):
    DEPMAN_LOGGER.info("Listing dependencies:")
    if not config.dependencies:
        DEPMAN_LOGGER.info("No dependencies found.")
    else:
        for dep in config.dependencies:
            DEPMAN_LOGGER.info(" - {dep.name} ({dep.version}): {dep.location}".format(dep=dep))


DEPMAN_COMMANDS = {
    'list': list_deps,
}


def run_depman(config):
    parse_depfile(config)

    if config.command is None:
        DEPMAN_LOGGER.warning("No command specified.")
    else:
        command_fn = DEPMAN_COMMANDS.get(config.command, None)
        if command_fn is None:
            DEPMAN_LOGGER.error("Unknown command '{0}'".format(config.command))
        command_fn(config)


def main():
    config = handle_args(sys.argv[1:])
    run_depman(config)


if __name__ == '__main__':
    main()
