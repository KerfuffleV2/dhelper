#!/usr/bin/env python3
#
# INSTRUCTIONS:
# First, read the disclaimer below.
# Required files (loaded from current directory):
#  cards.csv     - from https://docs.google.com/spreadsheets/d/1PhhMm1hx1pBxvmmXg_sRMzmYiKv1RihVytyK-tJAK00/view#gid=1980241403 (Card List)
#  tierlist.csv  - from https://docs.google.com/spreadsheets/d/1NH1i_nfPKhXO53uKYgJYICrTx_XSqDC88b2I3e0vsc0/edit#gid=316760914 (Tabulated Summary)
#  deck.lst      - Use Eternal's deck export function and then paste into a file.

# The CSV files will be automatically downloaded and saved to the current directy of they don't exist.
# They also may be manually created using the links above.
# To manually download, go to File -> Download As -> CSV with the correct page selected.

# For deck.lst, make a deck with your pool of cards then export it (even though it will be invalid).
# A deck can only have 150 cards at most so it may be necessary to add the first 150, export,
# clear the deck and add the rest and then just append the second result to the first.

# If you want colors then you need the colorama package: https://pypi.org/project/colorama/

# The application can make use of the readline library for tab completion and history if it's available.

# Legal disclaimer:
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import csv, re, sys, itertools, re, os.path, argparse, textwrap, shlex
import urllib, urllib.request, collections
from configparser import ConfigParser

try:
  import readline
except ImportError:
  readline = None
  pass


DEFAULTCONFIG = """
[version]
version = 20181012

[output]
perline = 4
padding = 30
namelen = 18

[cards]
# Output filename
filename = cards.csv
# Source can be "googledocs" (default) in which case gdkey and gdgids should be set or "local" to disable remote updates.
source = googledocs
# Key for the Google Document.
gdkey = 1PhhMm1hx1pBxvmmXg_sRMzmYiKv1RihVytyK-tJAK00
# Space separated if the Google Document has multiple pages.
gdgids = 1980241403

[tierlists]
use = flashtdc_new sunyveil flash_old konan_old
# Mode may be one of "first" or "average".
mode = first

[flashtdc_new]
filename = tierlist_flashtdc.csv
# Possible format values = simple sunyveil konan
format = simple
namecolumn = 1
ratingcolumn = 7
gdkey = 1NH1i_nfPKhXO53uKYgJYICrTx_XSqDC88b2I3e0vsc0
gdgids = 316760914

[sunyveil]
filename = tierlist_sunyveil.csv
format = sunyveil
# Ratings in order to convert S A B C D E to a scale of 0-5.
ratingconversion = 5.0 4.0 3.0 2.0 1.0 0.5
gdkey = 1IeAah8Lx-c1-rQcJ_sBx-z0Eedx_Cjz8jX13WC4YwVc
gdgids = 0 248050559 1781856700 1502338198 1730333942 1811749516 898622616
  1068747823 1458320154 407589498 52210957 1553639420 1238016565 1190042616

[flash_old]
filename = tierlist_flashold.csv
format = simple
namecolumn = 1
ratingcolumn = 8
gdkey = 1aU8aNh6u-75fv22_s4LGijCNHMIKlA3d_l-AiUn8GLI
gdgids = 110849218

[konan_old]
filename = tierlist_konanold.csv
format = konan
ratingconversion = S=5.0 A+=4.5 A=4.0 A-=3.5 B+=3.4 B=3.0 B-=2.8 C+=2.6 C=2.5 C-=2.2 D+=2.0 D=1.8 D-=1.5 F=0.5
gdkey = 1by6eaBpYP5Hdrc98q7xRar0ye1_jOy2zP3Jp1f8VzTg
gdgids = 1855443894 1981568523 210208637 1978666032 1420782532

[deckmode]
deck = deck.lst

[quarrymode]
deck = deck.lst
minimumunits = 14
maxcolors = 3
minimumplayable = 26
# If unset, cards without a tier value will be skipped.
unknownscore = off
"""


PERLINE = 4 # Number of cards to show per line.
PADLEN = 30 # Maximum length of card text including count, influence reqs, etc.
MAXNAMELEN = 18 # Maximum length of card name.


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

CFG = None

try:
  import colorama
  colorama.init(autoreset = True)
  Fore = colorama.Fore
  Back = colorama.Back
  Style = colorama.Style
  HAVECOLORS = True
except ImportError:
  HAVECOLORS = False
  class ColDummy(object):
    def __getattr__(self, key):
      if key and type(key) is str and key[0] != '_':
        return ''
      raise AttributeError('ColDummy: Not here')
  Fore = ColDummy()
  Back = ColDummy()
  Style = ColDummy()


STYLES = {
  'r': Style.RESET_ALL,
  'd': Style.DIM,
  'b': Style.BRIGHT,
  'n': Style.NORMAL,
  'fblack': Fore.BLACK,
  'fred': Fore.RED,
  'fgreen': Fore.GREEN,
  'fyellow': Fore.YELLOW,
  'fblue': Fore.BLUE,
  'fmagenta': Fore.MAGENTA,
  'fcyan': Fore.CYAN,
  'fwhite': Fore.WHITE,
  'bblack': Back.BLACK,
  'bred': Back.RED,
  'bgreen': Back.GREEN,
  'byellow': Back.YELLOW,
  'bblue': Back.BLUE,
  'bmagenta': Back.MAGENTA,
  'bcyan': Back.CYAN,
  'bwhite': Back.WHITE,
}

def cf(fmt, *args, **fkwargs):
  kwargs = { **fkwargs, **STYLES }
  return fmt.format(*args, **kwargs)


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


class Card(object):
  def __init__(self, name, cost, creq, rarity, ctype = None, text = None, dam = None, life = None):
    self.name = name
    self.cost = cost
    self.creq = creq.upper()
    self.rarity = rarity
    self.ctype = ctype
    self.text = text
    self.dam = dam
    self.life = life



class TierList(object):
  def __init__(self, name, scfg):
    self.name = name
    self.cfg = scfg
    self.tl = {}

  def expandName(self, n):
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
    fn = self.cfg['filename']
    nameidx = self.cfg.getint('namecolumn') - 1
    ratingidx = self.cfg.getint('ratingcolumn') - 1
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
  def __init__(self, name, scfg):
    self.rc = tuple(float(v) for v in scfg['ratingconversion'].split(None))
    if len(self.rc) != 6:
      raise ValueError('TierListSunyveil: Invalid number of values in rating conversion')
    super().__init__(name, scfg)

  def load(self):
    scfg = self.cfg
    fn = scfg['filename']
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
  def __init__(self, name, scfg):
    self.rc = dict((rk, float(rv)) for rk,rv in (v.split('=', 1) for v in scfg['ratingconversion'].split(None)))
    super().__init__(name, scfg)

  def load(self):
    scfg = self.cfg
    fn = scfg['filename']
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
        name = rowval
        names = self.expandName(name)
        for currname in names:
          tierdata[currname] = TierCard(currname, currtier)


class TierLists(object):
  __tlc = {
      'simple': TierListSimple,
      'sunyveil': TierListSunyveil,
      'konan': TierListKonan,
    }
  def __init__(self):
    self.tls = collections.OrderedDict()

  def register(self, name, scfg):
    tltyp = scfg.get('format')
    if tltyp is None:
      raise ValueError('TierLists: Format not set for {0}'.format(name))
    tlclass = self.__tlc.get(tltyp.lower())
    if tlclass is None:
      raise ValueError('TierLists: Unknown tierlist type {0} for {1}'.format(tltyp, name))
    self.tls[name] = tlclass(name, scfg)

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
    if len(matched) == 0:
      return None
    avgresult = sum(tc.rating for tc,_ in matched) / len(matched)
    sources = list(tl for _,tl in matched)
    return (avgresult, sources)


class RatedCard(Card):
  @classmethod
  def fromCard(cls, card, rating, sources):
    return cls(card.name, card.cost, card.creq, card.rarity, card.ctype, card.text, card.dam, card.life,
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


class DeckCard(object):
  def __init__(self, name, card, count = 1):
    self.name = name
    self.card = card
    self.count = count
    self.unrated = not card.sources


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
    if len(s) == 0:
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
    if len(self.colorfilter) == 0:
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
    return (card.cost >= costrange[0] and card.cost <= costrange[1])


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




def getGDCSV(fn, key, pagegids, force = False):
  if not force and os.path.isfile(fn):
    return True
  datalist = []
  for pagegid in pagegids:
    urifmt = 'https://docs.google.com/spreadsheets/d/{key}/export?format=csv&gid={pagegid}'
    uri = urifmt.format(key = key, pagegid = pagegid)
    print('** Fetching {fn} from: {uri}'.format(
      fn = fn, uri = uri))
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
    resp = opener.open(uri)
    data = resp.read()
    datalist.append(data)
  size = 0
  with open(fn, 'wb') as fp:
    for data in datalist:
      size += len(data)
      fp.write(data)
  print('** {0} created. Size: {1}.'.format(fn, size))


def checkLists(force = False):
  def sc2i(scfg):
    fn = scfg['filename']
    k = scfg['gdkey']
    gids = scfg['gdgids'].split(None)
    return (fn, (k, gids))
  for sectname in ['cards'] + CFG['tierlists']['use'].split(None):
    sect = CFG[sectname]
    stype = sect.get('source', fallback = 'googledocs')
    fn = sect['filename']
    if stype == 'googledocs':
      fn, csvi = sc2i(sect)
      try:
        getGDCSV(fn, *csvi, force = force)
      except Exception as err:
        print('!! Fetching or creating {0} failed. Error: {1}'.format(fn, err), file = sys.stderr)
        print('!! Bailing. :(', file = sys.stderr)
        sys.exit(1)
    elif stype == 'local':
      if not os.path.isfile(fn):
        print('!! List {listname} set to local but file {fn} does not exist.'.format(listname = sectname, fn = fn))
        sys.exit(1)
      continue
    else:
      print('!! Unknown source {source} for list {listname}.'.format(source = stype, listname = sectname))


def mkDeckCard(name, cards, count = 1):
  card = cards.get(name)
  if card is None:
    return None
  return DeckCard(name, card, count = count)


def loadRatedCards():
  checkLists()
  cards = loadCards()
  tls = loadTierLists()
  tlmode = CFG['tierlists'].get('mode', 'average').lower()
  if tlmode not in ('average', 'first'):
    raise ValueError('TierList mode must be one of average or first')
  avg = tlmode == 'average'
  return RatedCards(cards, tls, avg = avg)


def loadTierLists():
  tls = TierLists()
  for sectname in CFG['tierlists']['use'].split(None):
    scfg = CFG[sectname]
    tls.register(sectname, scfg)
  tls.load()
  return tls



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
  fn = CFG['cards']['filename']
  cards = {}
  with open(fn, 'r', encoding = 'utf-8') as fp:
    csvr = csv.reader(fp)
    for row in csvr:
      if len(row) < 19 or row[0] == 'Reg':
        continue
      _reg,_prem,_cset,fac,typ,styp,name,rarity,cost,c1,c2,c3,c4,c5,dam,life,text,_rel,_upd = row
      name = name.strip()
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
      cards[name] = Card(name, int(cost) if cost != '*' else '*', creq, rarity[0],
        ctype = typ, text = text, dam = dam, life = life)
  return cards


RARITYCOLORS = {
  'C': Style.NORMAL + Fore.WHITE,
  'U': Style.BRIGHT + Fore.GREEN,
  'P': Style.BRIGHT + Fore.MAGENTA,
  'R': Style.BRIGHT + Fore.BLUE,
  'L': Style.BRIGHT + Fore.YELLOW
}

COLORCOLORS = {
  'F': Style.NORMAL + Fore.RED,
  'T': Style.NORMAL + Fore.YELLOW,
  'J': Style.NORMAL + Fore.GREEN,
  'P': Style.NORMAL + Fore.BLUE,
  'S': Style.NORMAL + Fore.MAGENTA
}

TYPES = set(('Unit', 'Attachment', 'Spell', 'Fast Spell', 'Power', 'Sigil', 'Other'))
TYPECOLORS = {
  'Unit': Style.RESET_ALL,
  'Attachment': Style.BRIGHT + Fore.WHITE,
  'Spell': Style.NORMAL + Fore.CYAN,
  'Fast Spell': Style.BRIGHT + Fore.CYAN,
  'Power': Style.NORMAL + Fore.YELLOW,
  'Sigil': Style.DIM + Fore.YELLOW
}


def mkRatingColor(rating):
  if type(rating) is not float:
    return ''
  if rating > 3.5:
    return cf('{b}{fgreen}')
  elif rating > 3:
    return cf('{n}{fgreen}')
  elif rating > 2.5:
    return cf('{d}{fgreen}')
  elif rating > 2:
    return cf('{n}{fyellow}')
  elif rating > 1.5:
    return cf('{b}{fyellow}')
  elif rating > 1:
    return cf('{d}{fred}')
  elif rating > 0.5:
    return cf('{n}{fred}')
  return cf('{b}{fred}')


def mkRatingString(rating):
  if rating is None:
    return '?.??'
  if type(rating) is not float:
    return rating
  return '{0:1.2f}'.format(rating)


def mkCardText(deckcard, padlen = PADLEN, maxlen = MAXNAMELEN):
  card = deckcard.card
  name = deckcard.name
  if card is None:
    return name
  countstr = '' if deckcard.count < 2 else '{0}x'.format(deckcard.count)
  unstyled = '<{rarity}> {count}{name}:{cost}{creq}'.format(
    name = name[:maxlen], count = countstr,
    cost = card.cost, creq = card.creq, rarity = card.rarity)
  styledcreq = ''.join('{0}{1}{2}'.format(COLORCOLORS.get(c, ''), c, Style.RESET_ALL) for c in card.creq)
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
    for i in range(0, len(g), PERLINE):
      cardschunk = g[i:i + PERLINE]
      showncount += sum(card.count for card in cardschunk)
      if len(cardschunk) == 0:
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


def showTierList(deck, cardfilter = None, extratext = True, padding = ''):
  if len(deck) == 0:
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


def handleDraft(pargs):
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
      if len(deck) > 0:
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
      except Exception as err:
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
        cardstr = mkCardText(deckcard, maxlen = 100), r = Style.RESET_ALL, ratingcol = ratingcol,
        text = ctext)
    if deckcard.unrated:
      print('Not in tier list:{0}'.format(output))
    else:
      print(output)
    deck[cardname] = deckcard
  showTierList(deck)


def handleInteract(pargs):
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
    elif len(args) == 0:
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
    if pargs.filter is not None and len(pargs.filter) > 0:
      filtstr += ':' + pargs.filter
    filt = Filter.fromString(filtstr)
    fdeck = FilteredDeck.fromDeck(deckcards, filt)
    namesl = list(set(c.name for c in fdeck.deck if c.card.ctype != 'Power' and c.card.ctype != 'Sigil'))
    namesl.sort()
    names = tuple(namesl)
    if names in seen:
      continue
    seen.add(names)
    prettycolors = ''.join('{0}{1}{2}'.format(COLORCOLORS.get(c, ''), c, Style.RESET_ALL) for c in colors)
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
      CFG.write(fp, space_around_delimiters = True)
    else:
      fp.write(DEFAULTCONFIG)
  print('** Config file created:', fn)


def handleDumpTierList(pargs):
  cards = loadRatedCards()
  cw = csv.writer(sys.stdout, quoting = csv.QUOTE_NONNUMERIC)
  for card in cards.values():
    if card.sources:
      tr = card.rating
      if tr is not None and type(tr) is float:
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

def parseArgs(args = None):
  if args is None:
    args = sys.argv[1:]
  parser = argparse.ArgumentParser()
  subparsers = parser.add_subparsers(help = 'Use <SUBCOMMAND> --help for subcommand specific help')

  deck_parser = subparsers.add_parser('deck', aliases = ['d'], help = 'Deck mode',
    formatter_class = argparse.RawTextHelpFormatter)
  deck_parser.add_argument(action = 'store_const', dest = 'mode', const = 'deck', help = argparse.SUPPRESS)
  deck_parser.add_argument('-d', '--deck', metavar = '<DECKNAME>', type = str,
    default = CFG['deckmode']['deck'],
    help = 'Deck file, exported from Eternal (default deck.csv)')
  dmegroup = deck_parser.add_mutually_exclusive_group()
  dmegroup.add_argument('-f', '--filter', metavar = '<FILTER>', type = str, default = None,
    help = textwrap.dedent(FILTERHELP))
  dmegroup.add_argument('-c', '--cost', action = 'store_true', default = False,
    help = 'Group by cost (mutually exclusive with --filter)')

  draft_parser = subparsers.add_parser('draft', aliases = ['r'], help = 'Draft mode')
  draft_parser.add_argument(action = 'store_const', dest = 'mode', const = 'draft', help = argparse.SUPPRESS)

  interact_parser = subparsers.add_parser('interact', aliases = ['i'], help = 'Interactive mode')
  interact_parser.add_argument(action = 'store_const', dest = 'mode', const = 'interact', help = argparse.SUPPRESS)

  qcfg = CFG['quarrymode']
  quarry_parser = subparsers.add_parser('quarry', aliases = ['q'], help = 'Quarry mode (deck analysis)',
    formatter_class = argparse.RawTextHelpFormatter)
  quarry_parser.add_argument(action = 'store_const', dest = 'mode', const = 'quarry', help = argparse.SUPPRESS)
  quarry_parser.add_argument('-d', '--deck', metavar = '<DECKNAME>', type = str, default = qcfg['deck'],
    help = 'Deck file, exported from Eternal (default deck.csv)')
  qminunits = qcfg.getint('minimumunits')
  quarry_parser.add_argument('-u', '--units', metavar = '<NUM>', type = int,
    default = qminunits,
    help = 'Minimum units allowed (default {0}).'.format(qminunits))
  qmaxcolors = qcfg.getint('maxcolors')
  quarry_parser.add_argument('-m', '--maxcolors', metavar = '<NUM>', type = int,
    default = qmaxcolors,
    help = 'Maximum colors allowed (default {0}).'.format(qmaxcolors))
  qminplayable = qcfg.getint('minimumplayable')
  quarry_parser.add_argument('-p', '--playable', metavar = '<NUM>', type = int,
    default = qminplayable,
    help = 'Minimum playable cards allowed (default {0}).'.format(qminplayable))
  try:
    qunknownscore = qcfg.getboolean('unknownscore')
    if qunknownscore == False:
      qunknownscore = None
    else:
      qunknownscore = 1.0
  except ValueError:
    qunknownscore = qcfg.getfloat('unknownscore')
  quarry_parser.add_argument('-U', '--unknownscore', metavar = '<FLOAT>', type = float, default = None,
    help = 'Rating to assign to cards not in tierlist otherwise they are skipped (default {0}).'.format(
      'skipped' if qunknownscore is None else '{0:.2f}'.format(qunknownscore)
    ))
  quarry_parser.add_argument('-e', '--expand', action = 'store_true', default = False,
    help = 'Expand cards in each color.')
  quarry_parser.add_argument('-c', '--cost', action = 'store_true', default = False,
    help = 'Will expand cards by cost. Implies --expand.')
  quarry_parser.add_argument('-f', '--filter', metavar = '<FILTER>', type = str, default = None,
    help = textwrap.dedent('NOTE: Specifying color filters will likely cause issues here.\n' + FILTERHELP))

  update_parser = subparsers.add_parser('update', aliases = ['u'],
    help = 'Force update of cards.csv and tierlists')
  update_parser.add_argument(action = 'store_const', dest = 'mode', const = 'update')

  makeconfig_parser = subparsers.add_parser('makeconfig',
    help = 'Save the default config to dhelper.cfg')
  makeconfig_parser.add_argument(action = 'store_const', dest = 'mode', const = 'makeconfig')
  makeconfig_parser.add_argument('-m', '--merge', action = 'store_true', default = False,
    help = 'Merge existing config with default. WARNING! Will overwrite existing config file.')

  dumptl_parser = subparsers.add_parser('dumptierlist',
    help = 'Dump the tierlist value for each known card to the terminal in CSV format')
  dumptl_parser.add_argument(action = 'store_const', dest = 'mode', const = 'dumptierlist')

  argslen = len(args)
  if argslen == 0:
    args = ['interact']
  return parser.parse_args(args)


def loadConfig(fn = 'dhelper.cfg'):
  global CFG, PERLINE, PADLEN, MAXNAMELEN
  cfg = ConfigParser(empty_lines_in_values = False)
  cfg.read_string(DEFAULTCONFIG)
  cfg.read(['dhelper.cfg'])
  osec = cfg['output']
  CFG = cfg
  PERLINE = osec.getint('perline')
  PADLEN = osec.getint('padding')
  MAXNAMELEN = osec.getint('namelen')


def main():
  loadConfig()
  presult = parseArgs()
  handler = handlers.get(presult.mode)
  if handler is not None:
    print('')
    handler(presult)
    print('')
  else:
    print('!! The impossible happened, no handler for args:', presult, file = sys.stderr)
    sys.exit(1)


if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt:
    print('\n\nExit requested from keyboard.')
    sys.exit(0)