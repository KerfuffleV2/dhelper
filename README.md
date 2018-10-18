# Use case

This tool assists with drafting in the card game Eternal and also for evaluating the card pools in Sealed mode.

# Features

### Draft mode

You can enter card names (allows partial matches and tab completion) to see the tier list ratings. You enter sets of cards and then can see a list sorted by the ratings with information like cost/influence requirements visible.

##### Draft example:

![Draft example](https://raw.githubusercontent.com/KerfuffleV2/dhelper/assets/images/example-draft.png)

### Deck mode

You can display the cards in a deck sorted by rating or broken down by cost and rating.

##### Deck example:

![Deck example](https://raw.githubusercontent.com/KerfuffleV2/dhelper/assets/images/example-deck.png)

##### Deck by cost example:

![Draft example by cost](https://raw.githubusercontent.com/KerfuffleV2/dhelper/assets/images/example-deck-cost.png)

### Quarry mode

This is mostly useful for sealed. Given a pool of cards, it can show you average scores for a color combination and filter by colors where valid decks can be built. For example, it won't show color combinations with less than 14 units or 26 playable cards. These values are configurable.

##### Quarry example:
![Quarry example](https://raw.githubusercontent.com/KerfuffleV2/dhelper/assets/images/example-quarry.png)

##### Quarry example with cards:
![Quarry example by cost](https://raw.githubusercontent.com/KerfuffleV2/dhelper/assets/images/example-quarry-cost.png)

***

# Who it is useful for

Since it is a console-based application, it won't be useful for people that aren't comfortable at the commandline. It is a console-based Python script and should run on any platform Python 3 is supported (Linux, OS X, Windows, etc).

***

# Visual demo

Link here: https://asciinema.org/a/Gljx8zyc82ae6qQvYUxx741mH

# How use it

The source code is freely provided.

You will need a relatively recent version of Python 3: https://www.python.org/

If you want to see colors, the Colorama package will need to be installed: https://pypi.org/project/colorama/
