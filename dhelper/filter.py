__all__ = ['FILTERHELP', 'ColorFilter', 'Filter', 'FilteredDeck']

from .util import FACTIONS


FILTERHELP = '''\

A filter consists of multiple items separated by colon.

Rating:
  r<num> - Cards with rating less than <num> will be filtered.

Power cost:
  p<num>,<num> - Cards that don't fall in the range will be filtered.
  p<num> - Cards that cost more will be filtered.

Color:
  c<color1>,<color2>,<color3 etc> - May be a single color like T (time) or multiple like FT. "N" stands for neutral.
  Color prefixes:
  '=': Exact matching will be used. 'T' will no longer match 'TJ' and so on.
  '+': Exactly matches the colors but the amount needed is flexible. 'TJ' matches 'TTJ' but not 'TF'.
  '.': Matches as long as the requirement contains only colors from the filter definition.
       'TJ' matches 'TT' and 'JJ and 'TTJ' but not 'TJP'.

Example: r2.5:p5:cf,justice

This filter would show only:

1. Cards with rating greater or equal to 2.5
2. Power less or equal to 5.
3. Influence requirements including Fire or Justice.

'''


class ColorFilter(object):
  # Matches if the color appears anywhere in influence reqs.
  CFANY = 1
  # Matches as long as the colors match. Ex: TJ matches TJJ req but not TJP.
  CFCOLORS = 2
  # Only matches the exact requirement.
  CFEXACT = 3
  # Matches as long as the requirement contains only colors from the filter definition.
  # Ex: TJ matches TT, JJ, TTJJ but not S or TS.
  CFLOOSE = 4

  __COLORS = 'FTJPSN'

  @classmethod
  def fromString(cls, s):
    s = s.strip()
    if not s:
      return cls()
    s = s.upper()
    fc = s[0]
    if fc == '=':
      typ = cls.CFEXACT
      s = s[1:]
    elif fc == '+':
      typ = cls.CFCOLORS
      s = s[1:]
    elif fc == '.':
      typ = cls.CFLOOSE
      s = s[1:]
    else:
      typ = cls.CFANY
    if s == '':
      return cls()
    faction = FACTIONS.get(s.title())
    if faction is not None:
      return cls(color = faction, typ = typ)
    elif not all(c.upper() in cls.__COLORS for c in s):
      raise ValueError('Unknown color code in color filter.')
    return cls(color = s, typ = typ)


  def __init__(self, color = '', typ = None):
    self.color = color.upper()
    self.type = typ if typ is not None else self.CFANY


  def test(self, creq):
    if self.type == self.CFANY:
      cset = set(creq)
      return all(c in cset for c in set(self.color))
    elif self.type == self.CFEXACT:
      return creq == self.color
    elif self.type == self.CFCOLORS:
      return set(creq) == set(self.color)
    elif self.type == self.CFLOOSE:
      cset = set(self.color)
      return all(c in cset for c in set(creq))
    else:
      raise ValueError('Unhandled color filter type.')


class Filter(object):

  def __init__(self, ratinglimit = -100, costrange = (-100, 100),
    colorfilter = '', allowunknown = True):
    self.ratinglimit = ratinglimit
    self.allowunknown = allowunknown
    self.costrange = costrange
    self.colorfilter = colorfilter

  def __colorfiltf(self, card):
    if card is None:
      return False
    if not self.colorfilter:
      return True
    for cfentry in self.colorfilter:
      if cfentry.test(card.creq):
        return True
    return False


  def __costfiltf(self, card):
    if card is None:
      return False
    costrange = self.costrange
    if card.cost == '*':
      if costrange[0] > 0:
        return False
      return True
    return card.cost >= costrange[0] and card.cost <= costrange[1]


  @classmethod
  def fromString(cls, filterstr):
    filt = cls()
    for s in filterstr.strip().split(':'):
      s = s.strip()
      if s == '':
        continue
      if s[0] == 'r':
        filt.ratinglimit = float(s[1:])
      elif s[0] == 'p':
        powerparts = s[1:].split(',', 1)
        pplen = len(powerparts)
        if pplen == 0 or pplen > 2:
          raise ValueError('Bad power filter.')
        elif pplen == 1:
          filt.costrange = (-100, float(powerparts[0]))
        else:
          filt.costrange = (float(powerparts[0]), float(powerparts[1]))
      elif s[0] == 'c':
        cfilts = []
        for cpart in s[1:].split(','):
          cfilts.append(ColorFilter.fromString(cpart))
        filt.colorfilter = cfilts
      else:
        raise ValueError('Bad filter part: {0}'.format(s))
    return filt


  def test(self, dcard):
    card = dcard.card
    ok = (self.allowunknown and dcard.unrated) or \
      (not dcard.unrated and card.rating >= self.ratinglimit)
    ok = ok and self.__colorfiltf(card)
    ok = ok and self.__costfiltf(card)
    return ok


class FilteredDeck(object):
  def __init__(self, filt = Filter()):
    self.filter = filt
    self.known = 0
    self.unknown = 0
    self.deck = []

  @classmethod
  def fromDeck(cls, deck, cardfilter = Filter()):
    fdeck = cls(cardfilter)
    for card in deck.values():
      fdeck.addCard(card)
    return fdeck

  def __iter__(self):
    return self.deck.__iter__()


  def addCard(self, dcard):
    if not self.filter.test(dcard):
      return False
    self.deck.append(dcard)
    return True
