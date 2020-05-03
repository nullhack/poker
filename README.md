# poker_simulation

This module implements basic functions to evaluate poker games (in special, texas hold'em)

Example:

```Python
from card_games import TexasHoldem
p = TexasHoldem(num_players=5)
p.shuffle()
print(f'players: {p.players}')
print(f'table: {p.table}')
print(f'winners: {p.winners}')
print(f'evaluate hand of player 0: {p.evaluate_hand(p.player(0))}')
hand = ['6♣', '2♠', '6♠', '6♥', 'A♥', '8♦']
print(f'evaluate the hand {hand}: {p.evaluate_hand(hand)}')
```