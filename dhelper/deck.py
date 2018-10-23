__all__ = ['DeckCard', 'loadDeckCards', 'saveDeckCards']

import re
from .util import fixCardName


_MARKETMARKER = '--------------MARKET---------------'


class DeckCard(object):
  @classmethod
  def mk(cls, name, cards, count = 1, market = False):
    card = cards.get(name)
    if card is None:
      return None
    return cls(name, card, count = count, market = market)

  def __init__(self, name, card, count = 1, market = False):
    self.name = name
    self.card = card
    self.count = count
    self.unrated = not card.sources
    self.market = market

  def toEternalFormat(self):
    return '{count} {name} (Set{setid} #{cardid})'.format(count = self.count, name = self.name, setid = self.card.setid, cardid = self.card.cardid)


def saveDeckCards(fn, deckcards):
  with open(fn, 'w', encoding = 'utf-8') as fp:
    market = []
    for dc in deckcards:
      if dc.market:
        market.append(dc)
      else:
        print(dc.toEternalFormat(), file = fp)
    if market:
      print(_MARKETMARKER, file = fp)
      for dc in market:
        print(dc.toEternalFormat(), file = fp)


deckcardre = re.compile(r'^(\d+)\s+([^(]+\S)\s+(?:[(].*[)])\s*$')
def loadDeckCards(fn, cards):
  deckcards = {}
  market = False
  with open(fn, 'r', encoding = 'utf-8') as fp:
    for line in fp:
      line = line.strip()
      if line == '' or line[0] == '#':
        continue
      if line == _MARKETMARKER:
        market = True
        continue
      result = deckcardre.match(line)
      if result is None:
        print('Unknown:',line)
        continue
      count,cardname = result.groups()
      cardname = fixCardName(cardname)
      count = int(count)
      deckcard = deckcards.get(cardname)
      if deckcard is None:
        deckcard = DeckCard.mk(cardname, cards, count = count, market = market)
        if deckcard is None:
          print('WARNING: Unknown card:', cardname)
          continue
      else:
        deckcard.count += count
      deckcards[cardname] = deckcard
  return deckcards
