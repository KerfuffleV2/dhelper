__all__ = ['loadTierLists']

import collections
import csv

from .config import CFG
from .cards import Card
from .util import FACTIONS, CRESTS, fixCardName


class TierList(object):
  def __init__(self, tlcfg):
    self.name = tlcfg.name
    self.cfg = tlcfg
    self.tl = {}

  def expandName(self, n):
    n = fixCardName(n)
    nameparts = n.lower().split(None, 1)
    expandfac = lambda fmt: tuple(fmt.format(s) for s,c in FACTIONS.items() if len(c) > 1)
    if len(nameparts) == 1:
      return (n,)
    p1, p2 = nameparts
    if p1 == 'all':
      if p2 == 'banners':
        return expandfac('{0} Banner')
      elif p2 == 'influence strangers':
        return expandfac('{0} Stranger')
      elif p2 == 'crests':
        return tuple('Crest of {0}'.format(s) for s in CRESTS)

    return (n,)

  def load(self):
    raise NotImplementedError('Base TierList class does not implement load.')

  def get(self, name, default = None):
    return self.tl.get(name, default)

  def __len__(self):
    return len(self.tl)

  def __getitem__(self, key):
    return self.tl[key]

  def __contains__(self, key):
    return key in self.tl


class TierListSimple(TierList):
  def load(self):
    fn = self.cfg.filename
    nameidx = self.cfg.namecolumn - 1
    ratingidx = self.cfg.ratingcolumn - 1
    tierdata = {}
    self.tl = tierdata
    with open(fn, 'r', encoding = 'utf-8') as fp:
      csvr = csv.reader(fp)
      for row in csvr:
        rowlen = len(row)
        if rowlen < 1 or row[0] == '' or row[0] == 'Card':
          continue
        if rowlen <= nameidx or rowlen <= ratingidx:
          continue
        name = row[nameidx].strip()
        rating = row[ratingidx].strip()
        if not name or not rating:
          continue
        rating = float(rating)
        names = self.expandName(name)
        for currname in names:
          tierdata[currname] = TierCard(currname, rating)


class TierListSunyveil(TierList):
  def __init__(self, tlcfg):
    self.rc = tuple(float(v) for v in tlcfg.ratingconversion.split(None))
    if len(self.rc) != 6:
      raise ValueError('TierListSunyveil: Invalid number of values in rating conversion')
    super().__init__(tlcfg)

  def load(self):
    scfg = self.cfg
    fn = scfg.filename
    rc = self.rc
    tierdata = {}
    self.tl = tierdata
    with open(fn, 'r', encoding = 'utf-8') as fp:
      csvr = csv.reader(fp)
      for row in csvr:
        row = row[:6]
        if row == ['S', 'A', 'B', 'C', 'D', 'E']:
          continue
        for idx in range(6):
          name = row[idx]
          name = name.strip()
          if name == '':
            continue
          rating = rc[idx]
          names = self.expandName(name)
          for currname in names:
            tierdata[currname] = TierCard(currname, rating)


class TierListKonan(TierList):
  def __init__(self, tlcfg):
    self.rc = dict((rk, float(rv)) for rk,rv in (v.split('=', 1) for v in tlcfg.ratingconversion.split(None)))
    super().__init__(tlcfg)

  def load(self):
    scfg = self.cfg
    fn = scfg.filename
    rc = self.rc
    tierdata = {}
    self.tl = tierdata
    currtier = None
    with open(fn, 'r', encoding = 'utf-8') as fp:
      csvr = csv.reader(fp)
      for row in csvr:
        if len(row) != 1:
          continue
        rowval = row[0].strip()
        if not rowval:
          continue
        if len(rowval) < 3:
          currtier = rc.get(rowval)
          if currtier is None:
            print('!! Unknown tier value:', rowval)
          continue
        if currtier is None:
          print('!! Got entry with no tier value set. Bailing!')
          return None
        nextrowval = None
        if rowval[-1] in '-+':
          nextrowval = rowval[-2:]
          rowval = rowval[:-2].strip()
        name = rowval
        names = self.expandName(name)
        for currname in names:
          tierdata[currname] = TierCard(currname, currtier)
        if nextrowval is not None:
          currtier = rc.get(nextrowval)
          if currtier is None:
            print('!! Unknown tier value:', rowval)
          nextrowval = None



class TierLists(object):
  __tlc = {
      'simple': TierListSimple,
      'sunyveil': TierListSunyveil,
      'konan': TierListKonan,
    }
  def __init__(self):
    self.tls = collections.OrderedDict()

  def register(self, tlcfg):
    tltyp = tlcfg.format
    name = tlcfg.name
    if tltyp is None:
      raise ValueError('TierLists: Format not set for {0}'.format(name))
    tlclass = self.__tlc.get(tltyp.lower())
    if tlclass is None:
      raise ValueError('TierLists: Unknown tierlist type {0} for {1}'.format(tltyp, name))
    self.tls[name] = tlclass(tlcfg)

  def load(self):
    for tl in self.tls.values():
      tl.load()

  def get(self, name, avg = True):
    if not avg:
      for tl in self.tls.values():
        tc = tl.get(name)
        if tc is not None:
          return (tc.rating, [tl])
      return None
    matched = []
    for tl in self.tls.values():
      tc = tl.get(name)
      if tc is not None:
        matched.append((tc, tl))
    if not matched:
      return None
    avgresult = sum(tc.rating for tc,_ in matched) / len(matched)
    sources = list(tl for _,tl in matched)
    return (avgresult, sources)


class RatedCard(Card):
  @classmethod
  def fromCard(cls, card, rating, sources):
    return cls(card.name, card.cost, card.creq, card.rarity, card.setid, card.cardid, card.ctype, card.text, card.dam, card.life,
      rating = rating, sources = sources)

  def __init__(self, *args, rating = None, sources = None, **kwargs):
    super().__init__(*args, **kwargs)
    if rating is None or not sources:
      rating = -10.0
      sources = []
    self.rating = rating
    self.sources = sources


class RatedCards(object):
  def __init__(self, cards, tls, avg = True):
    self.cards = {}
    self.tls = tls
    for card in cards.values():
      name = card.name
      tresult = tls.get(name, avg = avg)
      if tresult:
        rating, sources = tresult
      else:
        rating = None
        sources = None
      self.cards[name] = RatedCard.fromCard(card, rating, sources)

  def get(self, name, default = None):
    return self.cards.get(name, default)

  def keys(self):
    return self.cards.keys()

  def values(self):
    return self.cards.values()

  def items(self):
    return self.cards.items()

  def __len__(self):
    return len(self.cards)

  def __getitem__(self, key):
    return self.cards[key]

  def __contains__(self, key):
    return key in self.cards


class TierCard(object):
  def __init__(self, name, rating):
    self.name = name
    self.rating = rating


def loadTierLists():
  tls = TierLists()
  for tlcfg in CFG.tierlists.lists:
    tls.register(tlcfg)
  tls.load()
  return tls
