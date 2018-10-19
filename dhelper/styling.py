__all__ = ['HAVECOLORS', 'STYLES', 'COLORCOLORS', 'RARITYCOLORS', 'TYPECOLORS', 'cf', 'mkRatingColor']

Fore = None
Back = None
Style = None
HAVECOLORS = False

try:
  import colorama
  colorama.init(autoreset = True)
  Fore = colorama.Fore
  Back = colorama.Back
  Style = colorama.Style
  HAVECOLORS = True
except ImportError:
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
