__all__ = ['DeckCard', 'mkDeckCard', 'loadDeckCards']

import re


class DeckCard(object):
  def __init__(self, name, card, count = 1):
    self.name = name
    self.card = card
    self.count = count
    self.unrated = not card.sources


def mkDeckCard(name, cards, count = 1):
  card = cards.get(name)
  if card is None:
    return None
  return DeckCard(name, card, count = count)


deckcardre = re.compile(r'^(\d+)\s+([^(]+\S)\s+(?:[(].*[)])\s*$')
def loadDeckCards(fn, cards):
  deckcards = {}
  with open(fn, 'r', encoding = 'utf-8') as fp:
    for line in fp:
      line = line.strip()
      if line == '' or line[0] == '#' or line == '--------------MARKET---------------':
        continue
      result = deckcardre.match(line)
      if result is None:
        print('Unknown:',line)
        continue
      count,cardname = result.groups()
      count = int(count)
      deckcard = deckcards.get(cardname)
      if deckcard is None:
        deckcard = mkDeckCard(cardname, cards, count)
        if deckcard is None:
          print('WARNING: Unknown card:', cardname)
          continue
      else:
        deckcard.count += count
      deckcards[cardname] = deckcard
  return deckcards

