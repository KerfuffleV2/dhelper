__all__ = ['Card', 'mkFacStr', 'loadCards']

import csv

from .util import FACTIONS, fixCardName
from .config import CFG


class Card(object):
  def __init__(self, name, cost, creq, rarity, setid, cardid, ctype = None, text = None, dam = None, life = None):
    self.name = name
    self.cost = cost
    self.creq = creq.upper()
    self.rarity = rarity
    self.ctype = ctype
    self.setid = setid
    self.cardid = cardid
    self.text = text
    self.dam = dam
    self.life = life


def mkFacStr(fcolors, *ccosts):
  result = []
  clen = len(fcolors)
  costlen = len(ccosts)
  for idx in range(clen):
    if idx >= clen or idx >= costlen or ccosts[idx] == '':
      break
    cost = int(ccosts[idx])
    result.append(fcolors[idx] * cost)
  if len(result) == 0:
    return 'N'
  return ''.join(result)


def loadCards():
  cardids = {}
  with open(CFG.cardids.filename, 'r', encoding = 'utf-8') as fp:
    csvr = csv.reader(fp)
    for setid, cardid, cardname in csvr:
      cardids[cardname] = (setid, cardid)
  cards = {}
  with open(CFG.cards.filename, 'r', encoding = 'utf-8') as fp:
    csvr = csv.reader(fp)
    for row in csvr:
      if len(row) < 19 or row[0] == 'Reg':
        continue
      _reg,_prem,_cset,fac,typ,styp,name,rarity,cost,c1,c2,c3,c4,c5,dam,life,text,_rel,_upd = row
      name = fixCardName(name.strip())
      if name == 'Talon Drive':
        name = 'Talon Dive'
      if fac != 'Multi':
        fcolors = FACTIONS.get(fac, '*')
      else:
        fcolors = '?????'
      if cost == '':
        cost = '*'
      if rarity == '':
        rarity = '?'
      creq = mkFacStr(fcolors, c1, c2, c3, c4, c5)
      if cost[-1] == '+':
        cost = cost[:-1]
      if typ == 'Spell' and styp == 'Fast':
        typ = 'Fast Spell'
      elif typ == 'Power' and styp == 'Sigil':
        typ = 'Sigil'
      if typ == 'Power' or typ == 'Sigil':
        creq = FACTIONS.get(fac, creq)
      idresult = cardids.get(name)
      if idresult is None:
        # print('Cannot get cardid for card: ', name)
        continue
      setid, cardid = idresult
      cards[name] = Card(name, int(cost) if cost != '*' else '*', creq, rarity[0], setid, cardid,
        ctype = typ, text = text, dam = dam, life = life)
  return cards
