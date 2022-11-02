import pytest
import core
import math
import ipdb
import random

def test_Card():
    C = core.Card(name="Carte simple")
    assert C.name == "Carte simple"

def test_CTACard():

    deck = []
    nb_cards = 10
    for i in range(nb_cards):
        C = core.CTACard(
                name=f"Carte{i}",
                value=100*i)
        deck.append(C)

    assert len(deck) == nb_cards

def test_CTACard_str():

    C = core.CTACard(
                name=f"Carte test",
                value=100)


    assert str(C) == '\x1b[1m\x1b[38;5;170mCarte test\x1b[0m | \x1b[1m\x1b[38;5;3m100\x1b[0m'

def test_game():
    deck = []
    nb_cards = 10
    for i in range(nb_cards):
        C = core.CTACard(
                name=f"Carte{i}",
                value=100*i)
        deck.append(C)
    
    game = core.Game()

    player = core.CTAPlayer(name="test", deck=deck)
    game.set_player1(player=player)

def test_play_card():
    deck = []
    nb_cards = 100
    for i in range(nb_cards):
        C = core.CTACard(
                name=f"Carte{i}",
                value=100*i,
                element="Element"+str(i),
                rarity="gold")
        deck.append(C)
    
    game = core.Game()

    player1 = core.CTAPlayer(name="p1", deck=deck)
    player2 = core.CTAPlayer(name="p2", deck=deck)

    game.set_player1(player=player1)
    game.set_player2(player=player2)
    
    passage = 0
    for x in range(4):
        for y in range(4):
            game.play_card(random.randint(1, 2), passage, y, x)
            game.board.grid[passage].owner = random.randint(1, 2)
            passage += 1


    assert game.check_game_finish() == True

