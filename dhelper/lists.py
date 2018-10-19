__all__ = ['loadRatedCards', 'checkLists']

import urllib
import urllib.request
import urllib.error
import sys
import os

from .config import CFG
from .cards import loadCards
from .tierlists import loadTierLists, RatedCards


def getGDCSV(fn, key, pagegids, force = False):
  if not force and os.path.isfile(fn):
    return
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
      fn, csvi = (l.filename, (l.gdkey, l.gdgids))
      try:
        getGDCSV(fn, *csvi, force = force)
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
