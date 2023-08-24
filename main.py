#!/usr/bin/env python3

import sys

from game import Game


game = Game(sys.argv[1:])

while True:
    game.send_input(input())
