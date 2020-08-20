#!/usr/bin/env python

import os
import sys
import argparse
import logging

from xrftomo import config #, __version__


LOG = logging.getLogger('xrftomo')


def init(args):
    if not os.path.exists(str(args.config)):
        config.write(str(args.config))
    else:
        raise RuntimeError("{0} already exists".format(args.config))

def rec(args):
    from xrftomo import reco
    reco.tomo(args)

def gui(args):
    try:
        from xrftomo import gui
        gui.main(args)
    except ImportError as e:
        LOG.error(str(e))

def instMenu(args):
    from xrftomo import menu_installer
    try:
        menu_installer.install_menu()
    except:
        print("Error installing menu")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', **config.SECTIONS['general']['config'])
    tomo_params = config.TOMO_PARAMS 
    gui_params = tomo_params + ('gui', )

    cmd_parsers = [
        ('init',        init,           (),                             "Create configuration file"),
        ('rec',         rec,            tomo_params,                    "Run tomographic reconstruction using the parameters selected with the GUI"),
        ('gui',         gui,            gui_params,                     "GUI for xrftomo tomographic reconstruction"),
        ('menu',        instMenu,       (),                             "installs desktop shortcut for XRFtomo software")
    ]

    subparsers = parser.add_subparsers(title="Commands", metavar='')

    for cmd, func, sections, text in cmd_parsers:
        cmd_params = config.Params(sections=sections)
        cmd_parser = subparsers.add_parser(cmd, help=text, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        cmd_parser = cmd_params.add_arguments(cmd_parser)
        cmd_parser.set_defaults(_func=func)

    args = config.parse_known_args(parser, subparser=True)
    log_level = logging.DEBUG if args.verbose else logging.INFO
    LOG.setLevel(log_level)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    LOG.addHandler(stream_handler)
    if args.log:
        file_handler = logging.FileHandler(args.log)
        file_handler.setFormatter(logging.Formatter('%(name)s:%(levelname)s: %(message)s'))
        LOG.addHandler(file_handler)

    try:
        config.log_values(args)
        args._func(args)
    except RuntimeError as e:
        LOG.error(str(e))
        sys.exit(1)


if __name__ == '__main__':
    main()

