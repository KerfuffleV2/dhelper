__all__ = ['loadRatedCards', 'checkLists']

import urllib
import urllib.request
import urllib.error
import sys
import os
import time

from .config import CFG
from .cards import loadCards
from .tierlists import loadTierLists, RatedCards


_GDURIFORMAT = 'https://docs.google.com/spreadsheets/d/{key}/export?format=csv&gid={pagegid}'
def getCSV(cfg, autoupdate = False, force = False):
  fn = cfg.filename
  if os.path.isfile(fn):
    if autoupdate is not False:
      now = time.time()
      mtime = os.path.getmtime(fn)
      age = now - mtime
      if age < autoupdate and not force:
        return
    elif not force:
      return
  if cfg.source == 'googledocs':
    uris = tuple(_GDURIFORMAT.format(key = cfg.gdkey, pagegid = pagegid) for pagegid in cfg.gdgids)
  elif cfg.source == 'uri':
    uris = (cfg.uri,)
  else:
    raise ValueError('Unknown source type in getCSV')
  datalist = []
  for uri in uris:
    print('** Fetching {fn} from: {uri}'.format(
      fn = fn, uri = uri))
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
    ua = 'DHelper+urllib'
    req = urllib.request.Request(uri, headers = {'User-Agent': ua })
    resp = opener.open(req)
    data = resp.read()
    datalist.append(data)
  size = 0
  with open(fn, 'wb') as fp:
    for data in datalist:
      size += len(data)
      fp.write(data)
  print('** {0} created. Size: {1}.'.format(fn, size))


def loadRatedCards():
  checkLists()
  cards = loadCards()
  tls = loadTierLists()
  tlmode = CFG.tierlists.mode
  avg = tlmode == 'average'
  return RatedCards(cards, tls, avg = avg)



def checkLists(force = False):
  for l in [CFG.cards, CFG.cardids] + CFG.tierlists.lists:
    stype = l.source
    fn = l.filename
    if stype == 'googledocs' or stype == 'uri':
      try:
        getCSV(l, autoupdate = CFG.general.autoupdate, force = force)
      except (IOError, urllib.error.URLError) as err:
        print('!! Fetching or creating {0} failed. Error: {1}'.format(fn, err), file = sys.stderr)
        print('!! Bailing. :(', file = sys.stderr)
        sys.exit(1)
    elif stype == 'local':
      if not os.path.isfile(fn):
        print('!! List {listname} set to local but file {fn} does not exist.'.format(listname = l.name, fn = fn))
        sys.exit(1)
      continue
    else:
      print('!! Unknown source {source} for list {listname}.'.format(source = stype, listname = l.name))
