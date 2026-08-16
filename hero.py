class Hero:
    def __init__(self, name: str, stack: int):
        self.name = name
        self.stack = stack # Number of chips the hero has before the hand starts
        self.holeCards = []
        self.position = None # Defines the position of the hero in the hand eg. SB
        self.allIn = False
        self.folded = False
        self.currentBet = 0 # Chips put into the pot on the CURRENT street
        self.totalCommitted = 0 # Chips put into the pot across the WHOLE hand
        self.isHuman = False # Only the seat(s) Table marks human should be True

    # Resets the hero's state for a new hand
    def resetForNewHand(self):
        self.holeCards = []
        self.position = None
        self.allIn = False
        self.folded = False
        self.currentBet = 0
        self.totalCommitted = 0

    # Resets the hero's state for a new street.
    # Though note that the state must perist: a player who folded on the flop is still folded on the turn.
    def resetForNewStreet(self):
        self.currentBet = 0

    def isEliminated(self):
        return self.stack <= 0

    # Places the hero's bet into the pot and updates their stack and bet amounts
    def putInPot(self, amount: int):
        amount = min(amount, self.stack) # If the hero doesn't have enough chips, they go all in
        self.stack -= amount
        self.currentBet += amount
        self.totalCommitted += amount
        if self.stack <= 0:
            self.allIn = True
        return amount

    def __repr__(self):
        return (f"Hero(name={self.name}, stack={self.stack}, holeCards={self.holeCards}, "
                f"position={self.position}, allIn={self.allIn}, folded={self.folded}, "
                f"currentBet={self.currentBet}, totalCommitted={self.totalCommitted})")