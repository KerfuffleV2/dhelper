__all__ = ['getModeHandler']

import shlex
import csv
import os
import sys

from .output import showTierList, showDeckByCost, mkRatingColor, mkRatingString, mkCardText
from .args import parseArgs
from .config import DEFAULTCONFIG, CFG
from .stats import Stats
from .filter import FILTERHELP, Filter, FilteredDeck
from .lists import checkLists, loadRatedCards
from .deck import loadDeckCards, mkDeckCard
from .util import COLORCOMBOS
from .styling import COLORCOLORS, cf



try:
  import readline
except ImportError:
  readline = None


def handleDeck(pargs):
  filt = Filter()
  costmode = pargs.cost
  deckfn = pargs.deck
  if not costmode and pargs.filter is not None:
    try:
      filt = Filter.fromString(pargs.filter)
    except Exception as err:
      print('!! Parsing filter failed: ', err)
      print(FILTERHELP)
      raise
  cards = loadRatedCards()
  print('Loading deck: {0}'.format(deckfn))
  deckcards = loadDeckCards(deckfn, cards)
  if not costmode:
    showTierList(deckcards, filt)
  else:
    showDeckByCost(deckcards)
    print('***  Summary: ', Stats(FilteredDeck.fromDeck(deckcards)).pretty())



def handleDraft(_pargs):
  cards = loadRatedCards()
  lccards = dict((k.lower(),k) for k in cards.keys())
  lckeys = list(lccards.keys())

  if readline is not None:
    ckeys = cards.keys()
    def rlcompleterf(line, state):
      if not line:
        result = [c for c in ckeys][state]
      else:
        result = [c for c in ckeys if c.lower().startswith(line.lower())][state]
      return result

    readline.parse_and_bind('tab: complete')
    readline.set_completer_delims('')
    readline.set_completer(rlcompleterf)

  deck = {}
  def findmatches(s):
    return list(k for k in lckeys if k.find(s) != -1)

  while True:
    try:
      line = input('\nEnter card or filter (!help for help): ')
    except EOFError:
      print('')
      break
    if line is None:
      break
    line = line.strip()
    if line == '':
      showTierList(deck)
      if deck:
        print('** Starting new set **')
      deck = {}
      continue
    if line[0] == '!':
      if line == '!help':
        print(FILTERHELP)
        print('A blank filter will show the current cards unfiltered.')
        print('!q or !quit will exit draft mode.')
        continue
      elif line == '!q' or line == '!quit':
        break
      try:
        filt = Filter.fromString(line[1:])
      except ValueError as err:
        print('! Error: Parsing filter failed: ', err)
        continue
      showTierList(deck, filt)
      continue
    elif line[0] == '#':
      continue
    matches = findmatches(line.lower())
    if not matches:
      print('Unknown', line)
      continue
    elif len(matches) > 1:
      if line not in cards:
        print('\nAmbiguous:', '; '.join(lccards[n] for n in matches))
        print('Enter complete name with capitalization for an exact match.')
        continue
      lccardname = line.lower()
    else:
      lccardname = matches[0]
    cardname = lccards.get(lccardname)
    if cardname is None:
      print('Unknown:', line)
      continue
    deckcard = mkDeckCard(cardname, cards)
    if deckcard is None:
      print('Unknown card:', cardname)
    else:
      c = deckcard.card
      ctext = '^^^ {ctype}{stats}: {text}'.format(
        stats = '({0}/{1})'.format(c.dam, c.life) if c.dam != '' else '',
        ctype = c.ctype,
        text = c.text)
      ratingcol = mkRatingColor(c.rating)
      output = '{ratingcol}{ratingstr:<5}{r}{cardstr}\n{r}{text}'.format(
        ratingstr = mkRatingString(c.rating) if c.rating >= 0 else '',
        cardstr = mkCardText(deckcard, maxlen = 100), r = cf('{r}'), ratingcol = ratingcol,
        text = ctext)
    if deckcard.unrated:
      print('Not in tier list:{0}'.format(output))
    else:
      print(output)
    deck[cardname] = deckcard
  showTierList(deck)


def handleInteract(_pargs):
  checkLists()
  while True:
    if readline is not None:
      readline.parse_and_bind('tab: off')
      readline.set_completer_delims('')
      readline.set_completer(None)
    try:
      line = input('\nDHelper (h for help): ')
    except EOFError:
      return
    line = line.strip()
    if line and line[0] == '#':
      continue
    args = shlex.split(line)
    if args == ['h']:
      args = ['--help']
    elif args == ['quit']:
      break
    elif not args:
      args = ['deck']
    elif len(args) > 1 and args[1][0] != '-':
      args[1] = '-' + args[1]
    try:
      presult = parseArgs(args)
    except SystemExit:
      continue
    if presult.mode == 'interact':
      print('?? You are already in interactive mode. It does not get any more interactive than this.')
      continue
    handler = handlers.get(presult.mode)
    if handler is not None:
      print('\n*** Entering {0} mode.\n'.format(presult.mode))
      handler(presult)
      print('\n*** Exiting {0} mode.\n'.format(presult.mode))
    else:
      print('Unknown command:', args)


def handleQuarry(pargs):
  deckfn = pargs.deck
  cards = loadRatedCards()
  print('Loading deck: {0}'.format(deckfn))
  deckcards = loadDeckCards(deckfn, cards)
  seen = set()
  colorscores = []
  for colors in COLORCOMBOS:
    if len(colors) > pargs.maxcolors:
      continue
    filtstr = 'c.n' + colors
    if pargs.filter:
      filtstr += ':' + pargs.filter
    filt = Filter.fromString(filtstr)
    fdeck = FilteredDeck.fromDeck(deckcards, filt)
    namesl = list(set(c.name for c in fdeck.deck if c.card.ctype != 'Power' and c.card.ctype != 'Sigil'))
    namesl.sort()
    names = tuple(namesl)
    if names in seen:
      continue
    seen.add(names)
    prettycolors = ''.join('{0}{1}{2}'.format(COLORCOLORS.get(c, ''), c, cf('{r}')) for c in colors)
    padding = ' ' * (5 - len(colors))
    stats = Stats(fdeck, unknownscore = pargs.unknownscore)
    if stats.typecounts['Unit'] < pargs.units:
      continue
    playablecount = sum(stats.typecounts.get(t, 0) for t in ('Unit', 'Spell', 'Fast Spell', 'Attachment'))
    if playablecount < pargs.playable:
      continue
    colorscores.append((stats.avgscore, prettycolors))
    print(cf('{padding}{colors}{d}:{r} {stats}', colors = prettycolors, padding = padding, stats = stats.pretty()))
    if pargs.expand or pargs.cost:
      if pargs.cost:
        showDeckByCost(deckcards, filtstr, padding = '    ')
      else:
        showTierList(deckcards, cardfilter = filt, extratext = False, padding = '    ')
        print()
    colorscores.sort(key = lambda i: i[0], reverse = True)


  print('\nScore ranking:',
    cf(', '.join(
      cf('{r}{col}{r}{d}({b}{fwhite}{score:.2f}{r}{d}){r}', col = col, score = score)
      for score,col in colorscores)))


def handleMakeConfig(pargs, fn = 'dhelper.cfg'):
  if os.path.exists(fn) and not pargs.merge:
    print('!! {0} already exists. Remove it if you want a new default config and then run this command again.'.format(fn))
    return
  with open('dhelper.cfg', 'w', encoding = 'utf-8') as fp:
    if pargs.merge:
      CFG.pcfg.write(fp, space_around_delimiters = True)
    else:
      fp.write(DEFAULTCONFIG)
  print('** Config file created:', fn)


def handleDumpTierList(_pargs):
  cards = loadRatedCards()
  cw = csv.writer(sys.stdout, quoting = csv.QUOTE_NONNUMERIC)
  for card in cards.values():
    if card.sources:
      tr = card.rating
      if tr is not None and isinstance(tr, float):
        otr = '{0:g}'.format(tr)
        ntr = '{0:.3f}'.format(tr)
        if len(ntr) < len(otr):
          tr = ntr
      row = (card.name, tr, ','.join(tl.name for tl in card.sources))
    else:
      row = [card.name, None, None]
    cw.writerow(row)



handlers = {
  'deck': handleDeck,
  'draft': handleDraft,
  'update': lambda pargs: checkLists(force = True),
  'interact': handleInteract,
  'quarry': handleQuarry,
  'makeconfig': handleMakeConfig,
  'dumptierlist': handleDumpTierList,
}


def getModeHandler(mode):
  return handlers.get(mode)


# TBD: actually verifying stuff.
