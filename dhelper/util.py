__all__ = ['FACTIONS', 'CTOFACTION', 'CRESTS', 'COLORCOMBOS', 'TYPES']

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
