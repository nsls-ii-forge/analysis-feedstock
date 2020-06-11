import argparse
import importlib
import logging
import subprocess
# import os
import sys
from distutils.version import LooseVersion
from subprocess import PIPE

logger = logging.getLogger(__name__)


def check_conda_channels(forbidden_channel='conda-forge',
                         cmd='conda list --show-channel-url'):
    """Check conda channels.

    This function checks if the list of channels does not have "forbidden"
    channels (useful for validation of the resulted packages from a feedstock).

    Parameters:
    -----------
    forbidden_channel: str, optional
        a channel to warn about if it is found in the package list in a conda
        environment
    cmd: str, optional
        a command to check a list of packages in a conda environment
    """

    # TODO: use later once https://github.com/conda/conda/pull/9998 resolved
    # (either merged or instructions how to properly use the function provided)
    # from conda.cli.main_list import list_packages
    # pkgs = list_packages(os.environ['CONDA_PREFIX'], show_channel_urls=True)
    # for p in pkgs[1]:
    #     if 'conda-forge' in p:
    #         print(p)

    res = subprocess.run(cmd.split(), stdout=PIPE, stderr=PIPE)
    pkgs = res.stdout.decode().split('\n')

    failed_packages = []
    for p in pkgs:
        if forbidden_channel in p:
            failed_packages.append(p)

    if failed_packages:
        formatted = '\n'.join(failed_packages)
        raise RuntimeError(f'Packages from the "{forbidden_channel}" channel '
                           f'found:\n{formatted}')
    else:
        print(f'No packages were installed from {forbidden_channel}.')


def check_package_version(package=None, expected_version=None):
    """Check package version.

    Parameters:
    -----------
    package: str
        a package to check the version for
    expected_version: str
        minimum expected version of the package
    """
    if package is None:
        raise ValueError(f'Wrong package name: {package}')
    if expected_version is None:
        raise ValueError(f'Wrong expected version: {expected_version}')

    pkg = importlib.import_module(package)
    pkg_version = pkg.__version__
    if LooseVersion(pkg_version) < expected_version:
        raise ValueError(f'The found version ("{pkg_version}") of "{package}" '
                         f'is less than the expected version '
                         f'({expected_version})')
    else:
        print(f'The found version ({pkg_version}) of "{package}" is more or '
              f'equal the expected version ({expected_version})')


def main():
    parser = argparse.ArgumentParser(
        description='Check various parameters of a generated conda package.')

    types_of_check = ('channels', 'version')

    # Type of the check
    parser.add_argument('-t', '--check-type', dest='check_type',
                        choices=types_of_check, default=None,
                        help=(f'a type of check to perform. One of '
                              f'{", ".join(types_of_check)}'))

    # Check channels
    parser.add_argument('-f', '--forbidden-channel', dest='forbidden_channel',
                        default='conda-forge', type=str,
                        help=('a channel to warn about if it is found in the '
                              'package list in a conda environment'))
    parser.add_argument('-c', '--cmd', dest='cmd',
                        default='conda list --show-channel-url', type=str,
                        help=('a command to check a list of packages in a '
                              'conda environment'))

    # Check versions
    parser.add_argument('-p', '--package', dest='package',
                        default=None, type=str,
                        help='a package to check the version for')
    parser.add_argument('-e', '--expected-version', dest='expected_version',
                        default=None, type=str,
                        help='minimum expected version of the package')

    args = parser.parse_args()

    if args.check_type is None:
        parser.print_help()

    if args.check_type == 'channels':
        channels_kwargs = {'forbidden_channel': args.forbidden_channel,
                           'cmd': args.cmd}
        check_conda_channels(**channels_kwargs)
    elif args.check_type == 'version':
        version_kwargs = {'package': args.package,
                          'expected_version': args.expected_version}
        check_package_version(**version_kwargs)


if __name__ == '__main__':
    sys.exit(main())
