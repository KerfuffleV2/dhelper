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

from dhelper.main import main

main()
