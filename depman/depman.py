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
import subprocess
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
    dependencies_dir = None


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
    subparsers.add_parser('init', help='Initializes the dependency dir')
    subparsers.add_parser('list', help='Lists all dependencies')
    subparsers.add_parser('update', help='Fetches all dependencies at their specified version')

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


def parse_config(config, depman_config):
    config.dependencies_dir = os.path.join(os.path.dirname(config.depfile), 'deps')
    if depman_config:
        config.dependencies_dir = depman_config.get('dependencies_dir', config.dependencies_dir)


def parse_depfile(config):
    if not os.path.exists(config.depfile):
        DEPMAN_LOGGER.error('Could not file depfile {0}'.format(config.depfile))
        return Config()

    with open(config.depfile, 'r') as f:
        depfile = json.load(f)
        f.close()

        depman_config = depfile.get('config', {})
        parse_config(config, depman_config)

        deplist = depfile.get('dependencies', [])
        if not deplist:
            DEPMAN_LOGGER.warning('Depfile has no dependencies.')
        config.dependencies = parse_deplist(deplist)


def init(config):
    if os.path.exists(config.dependencies_dir):
        if not os.path.isdir(config.dependencies_dir):
            DEPMAN_LOGGER.error("Path %s exists, but isn't a directory!", config.dependencies_dir)
            raise Exception
    else:
        os.makedirs(config.dependencies_dir)

    with open(os.path.join(config.dependencies_dir, '.depman'), 'wb') as f:
        f.write("\0".encode())


def list_deps(config):
    DEPMAN_LOGGER.info("Listing dependencies:")
    if not config.dependencies:
        DEPMAN_LOGGER.info("No dependencies found.")
    else:
        for dep in config.dependencies:
            DEPMAN_LOGGER.info(" - {dep.name} ({dep.version}): {dep.location}".format(dep=dep))


def update_dep(config, dep):
    dep_dir = os.path.join(config.dependencies_dir, dep.name)
    if os.path.exists(dep_dir):
        if os.path.isdir(dep_dir):
            cmd = ['git', 'fetch', 'origin', '-q']
            result = subprocess.run(cmd, cwd=dep_dir)
            if result.returncode != 0:
                DEPMAN_LOGGER.error(
                    "Error (exit code %d) when fetching dependency %s with command-line:\n%s",
                    result.returncode, dep.name, cmd
                )
            cmd = ['git', 'checkout', dep.version, '-q']
            result = subprocess.run(cmd, cwd=dep_dir)
            if result.returncode != 0:
                DEPMAN_LOGGER.error(
                    "Error (exit code %d) when switching to version/branch %s dependency %s with command-line:\n%s",
                    result.returncode, dep.version, dep.name, cmd
                )
        else:
            DEPMAN_LOGGER.error("Path %s exists, but isn't a directory!", dep_dir)
    else:
        DEPMAN_LOGGER.info("Checking out %s version %s from %s", dep.name, dep.version, dep.location)
        cmd = ['git', 'clone', dep.location, dep.name, '--recursive', '-q']
        if dep.version != 'HEAD':
            cmd += ['-b', dep.version]
        result = subprocess.run(cmd, cwd=config.dependencies_dir)
        if result.returncode != 0:
            DEPMAN_LOGGER.error(
                "Error (exit code %d) when checking out dependency %s with command-line:\n%s",
                result.returncode, dep.name, cmd
            )


def update_deps(config):
    init(config)
    # DEPMAN_LOGGER.info("")
    if not config.dependencies:
        DEPMAN_LOGGER.info("No dependencies found.")
    else:
        for dep in config.dependencies:
            update_dep(config, dep)


DEPMAN_COMMANDS = {
    'init': init,
    'list': list_deps,
    'update': update_deps,
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
