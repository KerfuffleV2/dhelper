__all__ = ['Stats']

from .styling import cf, TYPECOLORS
from .util import TYPES

class Stats(object):
  def __init__(self, deck, unknownscore = None):
    self.__reset()
    self.__analyze(deck, unknownscore = unknownscore)

  def __reset(self):
    self.known = 0
    self.unknown = 0
    self.typecounts = dict((t,0) for t in TYPES)
    self.avgscore = 0.0
    self.totalscore = 0.0

  def __analyze(self, deck, unknownscore = None):
    self.totalscore = 0.0
    count = 0
    for dcard in deck:
      card = dcard.card
      typ = card.ctype if card.ctype in TYPES else 'Other'
      if typ == 'Sigil':
        continue
      if dcard.unrated:
        self.unknown += dcard.count
      else:
        self.known += dcard.count
      if not dcard.unrated:
        self.totalscore += card.rating * dcard.count
        count += 1
      elif unknownscore is not None:
        self.totalscore += unknownscore * dcard.count
        count += 1
      tcount = self.typecounts.get(typ, 0)
      self.typecounts[typ] = tcount + dcard.count
    if count:
      self.avgscore = self.totalscore / count
    else:
      self.avgscore = 0.0

  def pretty(self):
    tns = ('Unit', 'Spell', 'Fast Spell', 'Attachment', 'Power')
    typecountstr = ' '.join(
      cf('{tc}{tn}{r}{fwhite}{d}{count:<2}{r}', tn = ''.join(
        tn[0] for tn in typ.split(None) if tn),
        count = self.typecounts[typ], tc = TYPECOLORS.get(typ, ''))
      for typ in tns)
    s = cf('Avg score: {fwhite}{avgscore:2.2f}{r}, Known/un: {fwhite}{known:2}{r}/{fwhite}{unknown:2}{r}, Types: {typecounts}{r}',
      known = self.known, unknown = self.unknown, avgscore = self.avgscore, totalscore = self.totalscore,
      typecounts = typecountstr)
    return s
