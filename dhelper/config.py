__all__ = ['DEFAULTCONFIG', 'Config', 'loadConfig']

from configparser import ConfigParser
from .util import parseTime

DEFAULTCONFIG = """
[version]
version = 20181012

[general]
# autoupdate may be "off" or a time specification in the format of <num><letter> where letter is one of s(econds), m(inutes), d(ays), (w)eeks. If not specified, the default is seconds.
autoupdate = 1d

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

[cardids]
# Output filename
filename = cardids.csv
# Source can be "googledocs" (default) in which case gdkey and gdgids should be set or "local" to disable remote updates.
source = uri
uri = https://gist.githubusercontent.com/KerfuffleV2/3955d0146ceb4d4d604d8e6d55771886/raw/9845bf1eb5869cb0e6777e6fa477da813d6a9974/cardids.csv


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


class Config(object):
  def __init__(self, **kwargs):
    for k,v in kwargs.items():
      setattr(self, k, v)


CFG = Config()

def makeConfigOutput(pcfg, cfg):
  scfg = Config()
  cfg.output = scfg
  osec = pcfg['output']
  scfg.perline = osec.getint('perline')
  scfg.padding = osec.getint('padding')
  scfg.maxnamelen = osec.getint('namelen')



def makeConfigModes(pcfg, cfg):
  ncfg = Config()
  cfg.modes = ncfg

  sec = pcfg['deckmode']
  dcfg = Config()
  ncfg.deck = dcfg
  dcfg.deck = sec['deck']

  sec = pcfg['quarrymode']
  qcfg = Config()
  ncfg.quarry = qcfg
  qcfg.deck = sec['deck']
  qcfg.minunits = sec.getint('minimumunits')
  qcfg.maxcolors = sec.getint('maxcolors')
  qcfg.minplayable = sec.getint('minimumplayable')
  try:
    qunknownscore = sec.getboolean('unknownscore')
    if qunknownscore is False:
      qunknownscore = None
    else:
      qunknownscore = 1.0
  except ValueError:
    qunknownscore = sec.getfloat('unknownscore')
  qcfg.unknownscore = qunknownscore



def makeConfigGeneral(pcfg, cfg):
  sec = pcfg['general']
  ncfg = Config()
  cfg.general = ncfg
  try:
    autoupdate = sec.getboolean('autoupdate', fallback = '1d')
    if autoupdate is True:
      autoupdate = '1d'
  except ValueError:
    autoupdate = sec.get('autoupdate', '1d')
  if autoupdate is False:
    ncfg.autoupdate = False
  else:
    ncfg.autoupdate = parseTime(autoupdate)
  return ncfg



def mclHelper(sec, cfg):
    stype = sec.get('source', fallback = 'googledocs').lower()
    fn = sec['filename']
    if stype == 'googledocs':
      cfg.gdkey = sec['gdkey']
      cfg.gdgids = sec.get('gdgids', fallback = '0').split(None)
    elif stype == 'local':
      pass
    elif stype == 'uri':
      cfg.uri = sec['uri']
    else:
      raise ValueError('Bad source type in tierlist/cards section')
    cfg.source = stype
    cfg.filename = fn


def makeConfigTierlists(pcfg, cfg):
  sec = pcfg['tierlists']
  ncfg = Config()
  cfg.tierlists = ncfg
  mode = sec.get('mode', fallback = 'average').lower()
  if mode not in ('average', 'first'):
    raise ValueError('TierList mode must be one of average or first')
  ncfg.mode = mode
  ncfg.use = sec.get('use', fallback = '').split(None)
  ncfg.lists = []
  for tlname in ncfg.use:
    tlsec = pcfg[tlname]
    tlcfg = Config()
    tlcfg.name = tlname
    tlformat = tlsec.get('format', fallback = 'simple')
    tlcfg.format = tlformat
    if tlformat == 'simple':
      tlcfg.namecolumn = tlsec.getint('namecolumn')
      tlcfg.ratingcolumn = tlsec.getint('ratingcolumn')
    elif tlformat == 'sunyveil':
      tlcfg.ratingconversion = tlsec['ratingconversion']
    elif tlformat == 'konan':
      tlcfg.ratingconversion = tlsec['ratingconversion']
    else:
      raise ValueError('Bad format type in tierlist definition')
    ncfg.lists.append(tlcfg)
    mclHelper(tlsec, tlcfg)


def makeConfigCards(pcfg, cfg):
  sec = pcfg['cards']
  ncfg = Config()
  ncfg.name = 'cards'
  cfg.cards = ncfg
  mclHelper(sec, ncfg)


def makeConfigCardIds(pcfg, cfg):
  sec = pcfg['cardids']
  ncfg = Config()
  ncfg.name = 'cardids'
  cfg.cardids = ncfg
  mclHelper(sec, ncfg)


def loadConfig():
  pcfg = ConfigParser(empty_lines_in_values = False)
  pcfg.read_string(DEFAULTCONFIG)
  pcfg.read(['dhelper.cfg'])
  CFG.pcfg = pcfg
  makeConfigOutput(pcfg, CFG)
  makeConfigGeneral(pcfg, CFG)
  makeConfigModes(pcfg, CFG)
  makeConfigCards(pcfg, CFG)
  makeConfigCardIds(pcfg, CFG)
  makeConfigTierlists(pcfg, CFG)
