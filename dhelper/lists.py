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
def getGDCSV(cfg, autoupdate = False, force = False):
  fn = cfg.filename
  if os.path.isfile(fn):
    if autoupdate is not False:
      now = time.time()
      mtime = os.path.getmtime(fn)
      age = now - mtime
      if now - mtime < autoupdate and not force:
        return
    elif not force:
      return
  datalist = []
  for pagegid in cfg.gdgids:
    uri = _GDURIFORMAT.format(key = cfg.gdkey, pagegid = pagegid)
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


def loadRatedCards():
  checkLists()
  cards = loadCards()
  tls = loadTierLists()
  tlmode = CFG.tierlists.mode
  avg = tlmode == 'average'
  return RatedCards(cards, tls, avg = avg)



def checkLists(force = False):
  for l in [CFG.cards] + CFG.tierlists.lists:
    stype = l.source
    fn = l.filename
    if stype == 'googledocs':
      try:
        getGDCSV(l, autoupdate = CFG.general.autoupdate, force = force)
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
