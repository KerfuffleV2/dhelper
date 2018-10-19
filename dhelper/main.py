import csv, re, sys, itertools, re, os.path, argparse, textwrap, shlex
import collections

from .config import loadConfig
from .util import *
from .modes import getModeHandler
from .args import parseArgs


def main():
  cfg = loadConfig()
  presult = parseArgs(cfg)
  handler = getModeHandler(presult.mode)
  if handler is not None:
    print('')
    handler(presult)
    print('')
  else:
    print('!! The impossible happened, no handler for args:', presult, file = sys.stderr)
    sys.exit(1)


if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt:
    print('\n\nExit requested from keyboard.')
    sys.exit(0)
