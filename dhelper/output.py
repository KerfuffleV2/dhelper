__all__ = ['mkRatingString', 'mkCardText', 'showRatingList', 'showDeckByCost', 'showTierList']

import itertools

from .config import CFG
from .filter import Filter, FilteredDeck
from .styling import RARITYCOLORS, COLORCOLORS, TYPECOLORS, mkRatingColor, cf
from .stats import Stats


def mkRatingString(rating):
  if rating is None:
    return '?.??'
  if not isinstance(rating, float):
    return rating
  return '{0:1.2f}'.format(rating)


def mkCardText(deckcard, padlen = None, maxlen = None):
  if padlen is None:
    padlen = CFG.output.padding
  if maxlen is None:
    maxlen = CFG.output.maxnamelen
  card = deckcard.card
  name = deckcard.name
  if card is None:
    return name
  countstr = '' if deckcard.count < 2 else '{0}x'.format(deckcard.count)
  unstyled = '<{rarity}> {count}{name}:{cost}{creq}'.format(
    name = name[:maxlen], count = countstr,
    cost = card.cost, creq = card.creq, rarity = card.rarity)
  styledcreq = ''.join('{0}{1}{2}'.format(COLORCOLORS.get(c, ''), c, cf('{r}')) for c in card.creq)
  typcolor = TYPECOLORS.get(card.ctype, '') if card.ctype is not None else ''
  styled = cf('{d}<{r}{rarecol}{rarity}{r}{d}>{r} {d}{count}{r}{typcol}{name}{r}{d}:{r}{b}{cost}{r}{creq}',
    rarecol = RARITYCOLORS.get(card.rarity, ''), typcol = typcolor,
    name = name[:maxlen], count = countstr, cost = card.cost, creq = styledcreq, rarity = card.rarity)
  result = ''.join((styled, ' ' * (padlen - len(unstyled)) if padlen != 0 else ''))
  return result


# Color filter example: 'T,TJ,N'
def showRatingList(deckcards, extratext = True, padding = ''):
  ratingf = lambda dcard: dcard.card.rating
  srl = sorted(deckcards, key = ratingf, reverse = True)
  gsrl = itertools.groupby(srl, ratingf)
  showncount = 0

  for rating,g in gsrl:
    if rating < 0:
      rating = '?.??'
    g = list(g)
    shownchunk = 0
    for i in range(0, len(g), CFG.output.perline):
      cardschunk = g[i:i + CFG.output.perline]
      showncount += sum(card.count for card in cardschunk)
      if not cardschunk:
        continue
      shownchunk += 1
      items = ' | '.join(mkCardText(deckcard) for deckcard in cardschunk)
      if shownchunk == 1:
        ratingstr = mkRatingString(rating)
        ratingcol = mkRatingColor(rating)
      else:
        ratingstr = ''
        ratingcol = ''
      print(cf('{padding}{ratingcol}{ratingstr:<5}{r}{items}',
         ratingstr = ratingstr, items = items, ratingcol = ratingcol, padding = padding))
  if extratext:
    print()
    print(Stats(deckcards).pretty())
  return showncount


def showDeckByCost(deckcards, cardfilter = None, padding = ''):
  for cr in ((-100,0), (1,1), (2,2), (3,3), (4,4), (5,5), (6,6), (7,7),(8,8),(9,9),(10,100)):
    if cardfilter is None:
      crfilt = Filter(costrange = cr)
    else:
      crfiltstr = 'p{0},{1}'.format(*cr)
      crfilt = Filter.fromString(':'.join((cardfilter, crfiltstr)))
    fdeck = showTierList(deckcards, cardfilter = crfilt, extratext = False, padding = padding)
    shown = len(fdeck.deck)
    if shown > 0:
      if cr[0] == cr[1]:
        coststr = str(cr[0])
      elif cr[0] < 1:
        coststr = '0'
      else:
        coststr = '>{0}'.format(cr[0] - 1)
      print(cf('{padding}{d}^^^  Power {b}{fwhite}{cost:>2}{r}: {stats}\n\n',
        cost = coststr, stats = Stats(fdeck).pretty(), padding = padding))



def showTierList(deck, cardfilter = None, extratext = True, padding = ''):
  if not deck:
    return
  if extratext:
    print('=' * 20, '\n')
  if cardfilter is None:
    cardfilter = Filter()
  filtdeck = FilteredDeck.fromDeck(deck, cardfilter = cardfilter)
  showRatingList(filtdeck, extratext = extratext, padding = padding)
  if extratext:
    print('=' * 20,'\n')
  return filtdeck
