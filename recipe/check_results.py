import argparse
# import os
import sys
import subprocess
import logging


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

    res = subprocess.run(cmd.split(), capture_output=True)
    pkgs = res.stdout.decode().split('\n')

    failed_packages = []
    for p in pkgs:
        if forbidden_channel in p:
            failed_packages.append(p)

    if failed_packages:
        formatted = '\n'.join(failed_packages)
        raise RuntimeError(f'Packages from the "{forbidden_channel}" channel '
                           f'found:\n{formatted}')


def main():
    parser = argparse.ArgumentParser(
        description='Check various parameters of a generated conda package.')
    parser.add_argument('-f', '--forbidden-channel', dest='forbidden_channel',
                        default='conda-forge',
                        help=('a channel to warn about if it is found in the '
                              'package list in a conda environment'))
    parser.add_argument('-c', '--cmd', dest='cmd',
                        default='conda list --show-channel-url',
                        help=('a command to check a list of packages in a '
                              'conda environment'))

    args = parser.parse_args()

    kwargs = {'forbidden_channel': args.forbidden_channel,
              'cmd': args.cmd}

    check_conda_channels(**kwargs)


if __name__ == '__main__':
    sys.exit(main())
