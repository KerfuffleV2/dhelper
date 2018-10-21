from html.parser import HTMLParser

import urllib
import urllib.request
import urllib.error
import csv
import operator

class EternalCardParser(HTMLParser):
  def __init__(self, *args, **kwargs):
    self.result = []
    self.snarf = None
    super().__init__(*args, **kwargs)

  def handle_starttag(self, tag, attrs):
    if tag == 'a':
      ad = dict(attrs)
      if 'data-set' in ad and 'data-eternalid' in ad:
        self.snarf = (int(ad['data-set']), int(ad['data-eternalid']))

  def handle_data(self, data):
    if self.snarf:
      self.result.append((self.snarf[0], self.snarf[1], data))
      self.snarf = None


def main():
  page = 0
  result = []
  while True:
    page += 1
    uri = 'https://eternalwarcry.com/cards?cardview=false&p={0}'.format(page)
    print('Fetching', uri)
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
    ua = 'DHelper+urllib'
    req = urllib.request.Request(uri, headers = {'User-Agent': ua })
    resp = opener.open(req)
    data = resp.read()
    parser = EternalCardParser()
    parser.feed(data.decode('utf-8'))
    if not parser.result:
      break
    result += parser.result
  sresult= sorted(result, key = operator.itemgetter(0, 1, 2))
  with open('cardids.csv', 'w') as outfp:
    cw = csv.writer(outfp, quoting = csv.QUOTE_NONNUMERIC)
    for row in sresult:
      if row[1] < 0:
        continue
      cw.writerow(row)


main()
