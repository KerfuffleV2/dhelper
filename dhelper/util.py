__all__ = ['FACTIONS', 'CTOFACTION', 'CRESTS', 'COLORCOMBOS', 'TYPES', 'parseTime', 'fixCardName']

import string


FACTIONS = {
  'Fire': 'F',
  'Time': 'T',
  'Justice': 'J',
  'Primal': 'P',
  'Shadow': 'S',
  'Praxis': 'FT',
  'Rakano': 'FJ',
  'Combrei': 'TJ',
  'Elysian': 'TP',
  'Hooru': 'JP',
  'Argenport': 'JS',
  'Skycrag': 'FP',
  'Feln': 'PS',
  'Stonescar': 'FS',
  'Xenan': 'TS',
  'Neutral': 'N'
}

CTOFACTION = dict((v,k) for k,v in FACTIONS.items())

CRESTS = {
  'Glory': 'Rakano',
  'Fury': 'Skycrag',
  'Chaos': 'Stonescar',
  'Impulse': 'Praxis',
  'Order': 'Hooru',
  'Vengeance': 'Argenport',
  'Cunning': 'Feln',
  'Progress': 'Combrei',
  'Wisdom': 'Elysian',
  'Mystery': 'Xenan'
}

COLORCOMBOS = ['T', 'J', 'P', 'S', 'F', 'TJ', 'TP', 'TS', 'TF', 'JP', 'JS', 'JF', 'PS', 'PF', 'SF', 'TJP', 'TJS', 'TJF', 'TPS', 'TPF', 'TSF', 'JPS', 'JPF', 'JSF', 'PSF', 'TJPS', 'TJPF', 'TJSF', 'TPSF', 'JPSF', 'TJPSF']

TYPES = set(('Unit', 'Attachment', 'Spell', 'Fast Spell', 'Power', 'Sigil', 'Other'))


_timeabbrevs = { 's': 1, 'm': 60, 'h': 3600, 'd': 86400, 'w': 604800 }
def parseTime(s):
  secsum = 0
  for tp in s.split(None):
    tp = tp.strip().lower()
    if not tp:
      continue
    lastchar = tp[-1]
    if lastchar in string.digits:
      secsum += int(tp)
      continue
    mult = _timeabbrevs.get(lastchar)
    if mult is None:
      raise ValueError('Bad time format')
    secsum += int(tp[:-1]) * mult
  return secsum


def fixCardName(s):
  return s.replace("’", "'")
