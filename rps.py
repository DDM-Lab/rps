import pyibl

# Note the non-standard payoffs for a Rock, Paper, Scissors game. Ties always pay 2 points,
# wins 3 or 4 depending upon which, and losses 0 or 1, depending upon which.
PAYOFFS = {"Rock":     {"Rock": 2, "Paper": 1, "Scissors": 4},
           "Paper":    {"Rock": 3, "Paper": 2, "Scissors": 1},
           "Scissors": {"Rock": 0, "Paper": 3, "Scissors": 2}}

def payoff(my_move, opp_move):
    return PAYOFFS[my_move][opp_move]

MOVES = list(PAYOFFS.keys())
PREPOPULATED = 5
ROUNDS = 200


class Player:
    """ Models a single player. The parameter, n, which should be a small, positive integer,
        is the number of opponet's moves to consult in forming a decision; that is, the most
        recent n such moves are consulted.
    """

    def __init__(self, n=1, noise=None, decay=None):
        self.lookback = n
        self.agent = pyibl.Agent(attributes=["move", "my_history", "opp_history"])
        if noise is not None:
            self.agent.noise = noise
        if decay is not None:
            self.agent.decay = decay
        for m in MOVES:
            self.agent.populate(PREPOPULATED, {"move": m,
                                               "my_history": (),
                                               "opp_history": ()})
            for mh in possible_histories(self.lookback):
                for oh in possible_histories(self.lookback):
                    self.agent.populate(PREPOPULATED, {"move": m,
                                                       "my_history": mh,
                                                       "opp_history": oh})
        self.reset()

    def reset(self):
        self.agent.reset(True)
        self.last_move = None
        self.my_moves = []
        self.opp_moves = []
        self.score = 0

    def my_choice(self):
        self.last_move = self.agent.choose(*[{"move": m,
                                              "my_history": tuple(self.my_moves),
                                              "opp_history": tuple(self.opp_moves)}
                                             for m in MOVES])
        self.my_moves.append(self.last_move["move"])
        self.my_moves = self.my_moves[-self.lookback:]
        return self.last_move

    def opp_move(self, om):
        self.opp_moves.append(om["move"])
        self.opp_moves = self.opp_moves[-self.lookback:]
        po = payoff(self.last_move["move"], om["move"])
        self.score += po
        self.agent.respond(po)
        return po


def possible_histories(n):
    if n == 1:
        return [("Rock",), ("Paper",), ("Scissors",)]
    prev = possible_histories(n - 1)
    result = list(prev)
    for p in prev:
        for m in MOVES:
            result.append((m,) + p)
    return result


def main():
    """ An example pitting two Players against one another, each consulting the most recent
        three rounds of recent history.
    """
    p1 = Player(3)
    p2 = Player(3)
    for i in range(ROUNDS):
        m1 = p1.my_choice()
        m2 = p2.my_choice()
        po1 = p1.opp_move(m2)
        po2 = p2.opp_move(m1)
        print(i + 1, m1["move"], m2["move"], po1, po2, p1.score, p2.score)


if __name__ == "__main__":
    main()
