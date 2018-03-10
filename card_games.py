import random
import itertools
import numpy

class Cards:
    
    def __init__(self, deck = None):
        self.ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
        self.suits = ['♣', '♦', '♥', '♠']
        self._start_ranks = 2
        self.ranks_weight = {self.ranks[i]:i+self._start_ranks for i in range(len(self.ranks))}
        self._start_suits = 1
        self.suits_weight = {self.suits[i]:i+self._start_suits for i in range(len(self.suits))}
        self.all = [
                '{}{}'.format(i[0], i[1])
                for i in list(itertools.product(self.ranks, self.suits))
            ]
        self.N = len(self.all)
        self.deck = deck if deck else random.sample(self.all, self.N)

    def shuffle(self, s=None, e=None):
        if not s or s<0: 
            s = 0
        if not e or e>self.N:
            e = self.N
        self.deck = self.deck[:s]+random.sample(self.deck[s:e], e-s)+self.deck[e:]


class Poker:

    cards = Cards()
    
    def __init__(self, num_players=2, my_deck=None):
        self.new_game(num_players, my_deck)

    def new_game(self, num_players=2, my_deck=None):
        self.cards = Cards(my_deck)
        if num_players * self.max_hand + self.max_table <= self.cards.N:
            self.num_players = num_players
        else:
            raise Exception("Not enough cards")

    def player(self, i):
        x = i*self.max_hand
        return self.cards.deck[x:x+self.max_hand] if i<self.num_players else []

    def players(self):
        return [self.player(i) for i in range(self.num_players)]

    def table(self):
        return self.cards.deck[-self.max_table:]

    def shuffle(self, nplayers=0, ntable=0):
        if nplayers<0 or nplayers>self.num_players: 
            nplayers = 0
        if ntable<0 or ntable>self.max_table: 
            ntable = 0
        self.cards.shuffle( nplayers*self.max_hand, self.cards.N - ntable )

    def set_game(self, players, table=[]):
        to_shuffle = set(self.cards.all)
        to_shuffle = to_shuffle.difference(table)
        hands = []
        for hand in players:
            hands += hand
        to_shuffle = list(to_shuffle.difference(hands))
        random.shuffle(to_shuffle)
        my_deck = hands + to_shuffle + table
        if not len(my_deck)==self.cards.N:
            raise Exception("Invalid game, check for repeated or invalid cards on hand/table")
        self.new_game(num_players=self.num_players, my_deck=my_deck)

    @classmethod
    def _sorted_rank(cls, H):
        return sorted(H, key=lambda k: cls.cards.ranks_weight[k[0]], reverse=True)

    @classmethod
    def _sorted_suit(cls, H):
        return sorted(H, key=lambda k: cls.cards.suits_weight[k[1]], reverse=True)
    
    @classmethod
    def sorted_hand(cls, H):
        return cls._sorted_rank(cls._sorted_suit(H))

    @classmethod
    def get_hands_dict(cls):
        return {
            (1, "highest rank"): cls.highest_rank,
            (2, "pair"): cls.highest_pair,
            (3, "two pairs"): cls.highest_2_pairs,
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
    def highest_2_pairs(cls, H, sort=True):
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
        H = cls.sorted_hand(H) if sort else H
        r = ([], H)
        v = [0, 0, 0, 0, 0, 0]
        v[5] = 4+cls.cards._start_ranks if H[0][0]==cls.cards.ranks[-1] else -1
        U,D,l = ([], [], [None])
        for h in H:
            if l[0]==h[0]:
                D.append(h)
            else:
                U.append(h)
                l = h
        for i in range(len(U)-4):
            for x in range(5):
                v[x] = cls.cards.ranks_weight[U[i+x][0]]+x
            if v[0]==v[1]==v[2]==v[3]==v[4]:
                r = (U[i:i+5], cls.sorted_hand(U[:i]+U[i+5:]+D))
                break
        if v[1]==v[2]==v[3]==v[4]==v[5]:
            r = (U[-4:]+U[:1], cls.sorted_hand(U[1:-4]+D))
        return r

    @classmethod
    def highest_flush(cls, H, sort=True):
        H = cls.sorted_hand(H) if sort else H
        r = ([], H)
        X = cls._sorted_suit(cls._sorted_rank(H))
        n = len(X)
        for i in range(n-4):
            if X[i][1]==X[i+1][1]==X[i+2][1]==X[i+3][1]==X[i+4][1]:
                r = (X[i:i+5], cls.sorted_hand(X[:i]+X[i+5:]))
                break
        return r

    #Refactor
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
        for suit in cls.cards.suits[::-1]:
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
        return (a,b) if a and a[1][0]==cls.cards.ranks[-2] else ([],H)

    @classmethod
    def evaluate_hand(cls, H, sort=True):
        H = cls.sorted_hand(H) if sort else H
        hands = cls.get_hands_dict()
        for key in sorted(hands.keys(), reverse=True):
            a,b = hands[key](H, False)
            if a: break
        return (key, cls.cards.ranks_weight[a[0][0]], cls.cards.suits_weight[a[0][1]])
    
    def evaluate_players(self):
        players = {}
        table = self.table()
        for i in range(self.num_players):
            players[i] = self.evaluate_hand(self.player(i)+table)
        return players
    
    def winners(self):
        raise Exception('Method not implemented')
    
    def winner(self):
        winners = self.winners()
        max_hand = max(winners.keys())
        return (max_hand, winners[max_hand])


class TexasHoldem(Poker):
    
    max_hand = 2

    max_table = 5
    
    def winners(self):
        evaluations = self.evaluate_players()
        winners = {}
        for k,v in evaluations.items():
            winners[v[:2]] = winners.get(v[:2],[]) + [k]
        return winners