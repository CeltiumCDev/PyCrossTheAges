import core
import ipdb

card = core.CTACard(
    name="truc",
    value=3000000000,
)

card_list = [core.CTACard(
    name="truc",
    value=3000000000,
), core.CTACard(
    name="truc",
    value=3000000000,
), core.CTACard(
    name="truc",
    value=3000000000,
), core.CTACard(
    name="truc",
    value=3000000000,
), core.CTACard(
    name="truc",
    value=3000000000,
)]



player  = core.player(name="player1", deck=card_list)
board = core.board()
board.set_card(x=2, y=2, card=core.CTACard(
    name="truc",
    value=3000000000,
))
print(board.display())

