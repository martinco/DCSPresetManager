import argparse
import sys
import os
import json
import logging

from PySide2.QtWidgets import QApplication

from .gui.main_window import MainGuiWindow
from .profiles import Profiles, Profile
from .mission import apply_profile, MissionError
from .utils import get_storage_dir
from . import logger, __version__

log = logger.get('app')


def gui(profiles):

    app = QApplication(sys.argv)
    window = MainGuiWindow(profiles)
    window.show()
    return app.exec_()


class MizFileDir(argparse.Action):

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise argparse.ArgumentError(self, 'nargs is not allowed')

        super().__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, value, option_string=None):
        # As we need to do the checks for gui and CLI, just check the basics
        # here and worry about catching the real error later to display it
        # appropriately

        if os.path.isdir(value):
            setattr(namespace, self.dest, value)
            return

        if not os.path.isfile(value):
            raise argparse.ArgumentError(self, 'No such file or directory: %s' % value)

        if not value.endswith('.miz'):
            raise argparse.ArgumentError(self, 'Invalid mission file extension, expecting miz')

        setattr(namespace, self.dest, os.path.abspath(value))


def main():

    p = argparse.ArgumentParser(
        description='Manage DCS Radios for the mission file',
        add_help=False
    )

    ap = p.add_argument_group('Processing Options')

    ap.add_argument(
        '-m',
        dest='mission_file',
        metavar='FILE',
        action=MizFileDir,
        help='DCS Mission file (.miz), or extracted directory to apply the profile to',
    )

    profile_group = ap.add_mutually_exclusive_group()

    profile_group.add_argument(
        '-j',
        dest='profile_json',
        metavar='FILE',
        type=argparse.FileType('r'),
        help='Explicit JSON profile instead of local profile',
    )

    profile_group.add_argument(
        '-p',
        dest='profile_name',
        metavar='PROFILE',
        help='Locally configured (gui) Profile to apply to the mission')

    profile_group.add_argument(
        '-l',
        dest='list_profiles',
        action='store_true',
        help='List available profiles (for use with -p)')

    lp = p.add_argument_group('Logging Options')

    lp.add_argument(
        '-v',
        help='Enable verbose messages',
        action='store_const',
        dest='loglevel',
        const=logging.INFO,
        default=logging.WARN,
    )

    lp.add_argument(
        '-d',
        help='Enable debugging messages',
        action='store_const',
        dest='loglevel',
        const=logging.DEBUG,
    )

    lp.add_argument(
        '-o',
        help='Log output file, default: %(default)s',
        dest='logfile',
        default=os.path.join(get_storage_dir(), 'log.txt'),
    )

    lp.add_argument(
        '-f',
        help='Also log to console',
        action='store_true',
        dest='foreground',
        default=False,
    )

    hp = p.add_argument_group('General Options')

    hp.add_argument(
        '-V',
        dest='print_version',
        action='store_true',
        help='Print version and exit'
    )

    hp.add_argument(
        '-h',
        action='help',
        help='show this help message and exit'
    )

    args = p.parse_args()

    if args.print_version:
        print(__version__)
        return 0

    # Make our logdir
    try:
        os.makedirs(os.path.dirname(args.logfile))
    except FileExistsError:
        pass

    # Setup Logging
    logger.add_file_logger(args.logfile)
    logging.root.setLevel(args.loglevel)

    if args.foreground:
        logger.add_stdout_logger()

    # Load profiles
    profiles = Profiles()

    if args.list_profiles:
        if not len(profiles):
            print('No profiles available')
            return 0

        print('\nAvailable Profiles:')
        for profile in profiles.keys():
            print('  %s' % profile)
        return 0

    source = args.profile_json or args.profile_name
    if ((args.mission_file and not source) or
            (source and not args.mission_file)):
        p.error('-m and either -p or -j must be specified for unattended usage')

    # Find our profile if were applying
    if args.mission_file:
        profile = None
        if args.profile_name:
            if args.profile_name not in profiles:
                p.error('Could not find profile: %s' % args.profile_name)
            profile = profiles[args.profile_name]
        elif args.profile_json:
            try:
                profile = Profile('External JSON', None, json.load(args.profile_json))
            except Exception as e:
                p.error('Invalid profile json: %s' % str(e))

        if not profile:
            p.error('Unable to determine profile')

        # Running command line, log to stdout by default
        logger.add_stdout_logger()

        try:
            update_summary = apply_profile(args.mission_file, profile)
        except MissionError as e:
            log.error(str(e))
            p.error(str(e))
            return 1

        print('\nSuccessfully updated:')
        pad = max(len(x) for x in update_summary.keys())+1
        for key, value in update_summary.items():
            print('  {key:{pad}} {value}'.format(
                key='%s:' % key,
                pad=pad,
                value=value,
            ))
        return 0

    # Initiate our Profiles with our container
    return gui(profiles)


if __name__ == '__main__':
    sys.exit(main())
