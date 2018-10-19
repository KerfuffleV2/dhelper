import sys

from .config import loadConfig
from .modes import getModeHandler
from .args import parseArgs


def main():
  loadConfig()
  presult = parseArgs()
  handler = getModeHandler(presult.mode)
  if handler is None:
    print('!! The impossible happened, no handler for args:', presult, file = sys.stderr)
    sys.exit(1)
  print('')
  try:
    handler(presult)
  except KeyboardInterrupt:
    print('\n\nExit requested from keyboard.')
    sys.exit(0)
  print('')


if __name__ == '__main__':
  main()