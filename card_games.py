import random
import itertools
import numpy


class Deck:
    """Defines a regular 52 card deck and default operations
    """
    
    def __init__(self):
        self.ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
        self.suits = ['♣', '♦', '♥', '♠']
        self._start_ranks = 2
        self.ranks_weight = {self.ranks[i]:i+self._start_ranks for i in range(len(self.ranks))}
        self._start_suits = 1
        self.suits_weight = {self.suits[i]:i+self._start_suits for i in range(len(self.suits))}
        self.cards = [
                '{}{}'.format(i[0], i[1])
                for i in list(itertools.product(self.ranks, self.suits))
            ]
        self.N = len(self.cards)
        self.stack = random.sample(self.cards, self.N)

    @property
    def stack(self):
        return self._stack
    
    @stack.setter
    def stack(self, new_stack):
        self._stack = new_stack
        self.N = len(self._stack)
        
    def shuffle(self, s=None, e=None):
        if e<s:
            raise Exception('e cannot be smaller than s')
        if not s or s<0: 
            s = 0
        if not e or e>self.N:
            e = self.N
        self.stack = self.stack[:s] + random.sample(self.stack[s:e], e-s) + self.stack[e:]

    def __getitem__(self, key=None):
        return self.stack[key]
    
    def __repr__(self):
        return str(self.stack)


class Poker:
    """ Defines a general poker game and methods to evaluate the game
    """
    deck = Deck()
    max_draw = 5
    max_table = 0
    max_hand = 5
    
    def __init__(self, num_players=2, my_deck=None):
        self.deck = Deck()
        self.new_game(num_players, my_deck)

    def new_game(self, num_players=2, my_deck=None):
        if my_deck:
            self.deck.stack = my_deck
        if num_players * self.max_draw + self.max_table <= self.deck.N:
            self.num_players = num_players
        else:
            raise Exception("Not enough cards in the deck")

    def player(self, i):
        x = i*self.max_draw
        return self.deck[x:x+self.max_draw] if i<self.num_players else []

    @property
    def players(self):
        return [self.player(i) for i in range(self.num_players)]

    @property
    def table(self):
        return self.deck[self.deck.N-self.max_table:]

    def shuffle(self, nplayers=0, ntable=0):
        if nplayers<0 or nplayers>self.num_players: 
            nplayers = 0
        if ntable<0 or ntable>self.max_table: 
            ntable = 0
        self.deck.shuffle( nplayers*self.max_draw, self.deck.N - ntable )

    @classmethod
    def _sorted_rank(cls, H):
        return sorted(H, key=lambda k: cls.deck.ranks_weight[k[0]], reverse=True)

    @classmethod
    def _sorted_suit(cls, H):
        return sorted(H, key=lambda k: cls.deck.suits_weight[k[1]], reverse=True)
    
    @classmethod
    def sorted_hand(cls, H):
        return cls._sorted_rank(cls._sorted_suit(H))

    @classmethod
    def get_hand_categories(cls):
        return {
            (1, "highest rank"): cls.highest_rank,
            (2, "pair"): cls.highest_pair,
            (3, "two pairs"): cls.highest_two_pairs,
            (4, "three"): cls.highest_three,
            (5, "straight"): cls.highest_straight,
            (6, "flush"): cls.highest_flush,
            (7, "full house"): cls.highest_full_house,
            (8, "four"): cls.highest_four,
            (9, "straight flush"): cls.highest_straight_flush,
            (10,"royal straight flush"): cls.highest_royal_straight_flush
        }
        
    @classmethod
    def highest_rank(cls, H, sort=True):
        H = cls.sorted_hand(H) if sort else H
        return (H[:1], H[1:])

    @classmethod
    def highest_pair(cls, H, sort=True):
        H = cls.sorted_hand(H) if sort else H
        r = ([], H)
        n = len(H)
        for i in range(n-1):
            if H[i][0]==H[i+1][0]:
                r = (H[i:i+2], H[:i]+H[i+2:])
                break
        return r

    @classmethod
    def highest_two_pairs(cls, H, sort=True):
        H = cls.sorted_hand(H) if sort else H
        a,b = cls.highest_pair(H, False)
        c,d = cls.highest_pair(b, False) if a else ([], [])
        r = (a+c, d) if c else ([], H)
        return r

    @classmethod
    def highest_three(cls, H, sort=True):
        H = cls.sorted_hand(H) if sort else H
        r = ([], H)
        n = len(H)
        for i in range(n-2):
            if H[i][0]==H[i+1][0]==H[i+2][0]:
                r = (H[i:i+3], H[:i]+H[i+3:])
                break
        return r

    @classmethod
    def highest_straight(cls, H, sort=True):
        # The idea is: move duplicates to D
        # Check if there's a sequence of consecutive numbers in U
        # Handle special case of 'A'
        H = cls.sorted_hand(H) if sort else H
        r = ([], H)
        v = [0, 0, 0, 0, 0, 0]
        v[5] = 4+cls.deck._start_ranks if H[0][0]==cls.deck.ranks[-1] else -1
        U,D,l = ([], [], [None])
        for h in H:
            if l[0]==h[0]:
                D.append(h)
            else:
                U.append(h)
                l = h
        for i in range(len(U)-4):
            for x in range(5):
                v[x] = cls.deck.ranks_weight[U[i+x][0]]+x
            if v[0]==v[1]==v[2]==v[3]==v[4]:
                r = (U[i:i+5], cls.sorted_hand(U[:i]+U[i+5:]+D))
                break
        if v[1]==v[2]==v[3]==v[4]==v[5]:
            r = (U[-4:]+U[:1], cls.sorted_hand(U[1:-4]+D))
        return r

    @classmethod
    def highest_flush(cls, H, sort=True):
        # The idea is: sort cards by suit,rank
        # try to find a sequence of 5 consecutive of same suit
        H = cls.sorted_hand(H) if sort else H
        r = ([], H)
        X = cls._sorted_suit(cls._sorted_rank(H))
        n = len(X)
        for i in range(n-4):
            if X[i][1]==X[i+1][1]==X[i+2][1]==X[i+3][1]==X[i+4][1]:
                r = (X[i:i+5], cls.sorted_hand(X[:i]+X[i+5:]))
                break
        return r

    @classmethod
    def highest_full_house(cls, H, sort=True):
        H = cls.sorted_hand(H) if sort else H
        a,b = cls.highest_three(H, False)
        c,d = cls.highest_pair(b, False) if a else ([], [])
        return (a+c, d) if c else ([], H)

    @classmethod
    def highest_four(cls, H, sort=True):
        H = cls.sorted_hand(H) if sort else H
        r = ([], H)
        n = len(H)
        for i in range(n-3):
            if H[i][0]==H[i+1][0]==H[i+2][0]==H[i+3][0]:
                r = (H[i:i+4], H[:i]+H[i+4:])
                break
        return r

    @classmethod
    def highest_straight_flush(cls, H, sort=True):
        H = cls.sorted_hand(H) if sort else H
        r = ([], H)
        for suit in cls.deck.suits[::-1]:
            U = [i for i in H if i[1]==suit]
            if len(U)>=5:
                D = [i for i in H if i[1]!=suit]
                a,b = cls.highest_straight(U, False)
                r = (a, cls.sorted_hand(D+b))
                break
        return r

    @classmethod
    def highest_royal_straight_flush(cls, H, sort=True):
        H = cls.sorted_hand(H) if sort else H
        a,b = cls.highest_straight_flush(H, False)
        return (a,b) if a and a[1][0]==cls.deck.ranks[-2] else ([],H)

    @classmethod
    def evaluate_hand(cls, H, sort=True):
        H = cls.sorted_hand(H) if sort else H
        hand_categories = cls.get_hand_categories()
        for key in sorted(hand_categories.keys(), reverse=True):
            a,b = hand_categories[key](H, False)
            if a: break
        return (key, 
                tuple(cls.deck.ranks_weight[h[0]] for h in a), 
                tuple(cls.deck.ranks_weight[h[0]] for h in b), 
                tuple(cls.deck.suits_weight[h[1]] for h in a), 
                tuple(cls.deck.suits_weight[h[1]] for h in b)
               )

    def evaluate_players(self):
        players = {}
        table = self.table
        for i in range(self.num_players):
            players[i] = self.evaluate_hand(self.player(i)+table)
        return players
    
    @property
    def winners(self):
        evaluations = self.evaluate_players()
        M = max([v[0]+(v[1]+v[2])[:self.max_hand] for k,v in evaluations.items()])
        winners = {}
        for k,v in evaluations.items():
            value = v[0]+(v[1]+v[2])[:self.max_hand]
            if value == M:
                winners[k] = v
        return winners
    
    @property
    def winner(self):
        return self.winners.popitem()


class TexasHoldem(Poker):
    max_draw = 2
    max_table = 5
    max_hand = 5