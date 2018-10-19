__all__ = ['parseArgs']

import sys, argparse, textwrap

from .filter import FILTERHELP
from .config import CFG


def parseArgs(args = None):
  cfg = CFG
  if args is None:
    args = sys.argv[1:]
  parser = argparse.ArgumentParser()
  subparsers = parser.add_subparsers(help = 'Use <SUBCOMMAND> --help for subcommand specific help')

  deck_parser = subparsers.add_parser('deck', aliases = ['d'], help = 'Deck mode',
    formatter_class = argparse.RawTextHelpFormatter)
  deck_parser.add_argument(action = 'store_const', dest = 'mode', const = 'deck', help = argparse.SUPPRESS)
  deck_parser.add_argument('-d', '--deck', metavar = '<DECKNAME>', type = str,
    default = cfg.modes.deck.deck,
    help = 'Deck file, exported from Eternal (default deck.csv)')
  dmegroup = deck_parser.add_mutually_exclusive_group()
  dmegroup.add_argument('-f', '--filter', metavar = '<FILTER>', type = str, default = None,
    help = textwrap.dedent(FILTERHELP))
  dmegroup.add_argument('-c', '--cost', action = 'store_true', default = False,
    help = 'Group by cost (mutually exclusive with --filter)')

  draft_parser = subparsers.add_parser('draft', aliases = ['r'], help = 'Draft mode')
  draft_parser.add_argument(action = 'store_const', dest = 'mode', const = 'draft', help = argparse.SUPPRESS)

  interact_parser = subparsers.add_parser('interact', aliases = ['i'], help = 'Interactive mode')
  interact_parser.add_argument(action = 'store_const', dest = 'mode', const = 'interact', help = argparse.SUPPRESS)

  qcfg = cfg.modes.quarry
  quarry_parser = subparsers.add_parser('quarry', aliases = ['q'], help = 'Quarry mode (deck analysis)',
    formatter_class = argparse.RawTextHelpFormatter)
  quarry_parser.add_argument(action = 'store_const', dest = 'mode', const = 'quarry', help = argparse.SUPPRESS)
  quarry_parser.add_argument('-d', '--deck', metavar = '<DECKNAME>', type = str, default = qcfg.deck,
    help = 'Deck file, exported from Eternal (default deck.csv)')
  qminunits = qcfg.minunits
  quarry_parser.add_argument('-u', '--units', metavar = '<NUM>', type = int,
    default = qminunits,
    help = 'Minimum units allowed (default {0}).'.format(qminunits))
  qmaxcolors = qcfg.maxcolors
  quarry_parser.add_argument('-m', '--maxcolors', metavar = '<NUM>', type = int,
    default = qmaxcolors,
    help = 'Maximum colors allowed (default {0}).'.format(qmaxcolors))
  qminplayable = qcfg.minplayable
  quarry_parser.add_argument('-p', '--playable', metavar = '<NUM>', type = int,
    default = qminplayable,
    help = 'Minimum playable cards allowed (default {0}).'.format(qminplayable))
  qunknownscore = qcfg.unknownscore
  quarry_parser.add_argument('-U', '--unknownscore', metavar = '<FLOAT>', type = float, default = None,
    help = 'Rating to assign to cards not in tierlist otherwise they are skipped (default {0}).'.format(
      'skipped' if qunknownscore is None else '{0:.2f}'.format(qunknownscore)
    ))
  quarry_parser.add_argument('-e', '--expand', action = 'store_true', default = False,
    help = 'Expand cards in each color.')
  quarry_parser.add_argument('-c', '--cost', action = 'store_true', default = False,
    help = 'Will expand cards by cost. Implies --expand.')
  quarry_parser.add_argument('-f', '--filter', metavar = '<FILTER>', type = str, default = None,
    help = textwrap.dedent('NOTE: Specifying color filters will likely cause issues here.\n' + FILTERHELP))

  update_parser = subparsers.add_parser('update', aliases = ['u'],
    help = 'Force update of cards.csv and tierlists')
  update_parser.add_argument(action = 'store_const', dest = 'mode', const = 'update')

  makeconfig_parser = subparsers.add_parser('makeconfig',
    help = 'Save the default config to dhelper.cfg')
  makeconfig_parser.add_argument(action = 'store_const', dest = 'mode', const = 'makeconfig')
  makeconfig_parser.add_argument('-m', '--merge', action = 'store_true', default = False,
    help = 'Merge existing config with default. WARNING! Will overwrite existing config file.')

  dumptl_parser = subparsers.add_parser('dumptierlist',
    help = 'Dump the tierlist value for each known card to the terminal in CSV format')
  dumptl_parser.add_argument(action = 'store_const', dest = 'mode', const = 'dumptierlist')

  argslen = len(args)
  if argslen == 0:
    args = ['interact']
  return parser.parse_args(args)

