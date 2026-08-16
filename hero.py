class Hero:
    def __init__(self, name:str, stack: int):
        self.name = name
        self.stack = stack #Number of chips the hero has before the hand starts
        self.holeCards = []
        self.position = None #Defines the position of the hero in the hand eg. SB
        self.isAllIn = False
        self.isFolded = False
        self.streetBet = 0 #Amount of chips the hero has put into the pot in the current hand (street)
        self.totalBet = 0 #Amount of chips the hero has put into the pot in the current hand and previous hands (whole hand)
        self.isHuman = True #If True, the engine will ask a real person what to do instead of a bot

    #Resets the hero's state for a new hand
    def resetNewHand(self):
        self.holeCards = []
        self.position = None
        self.isAllIn = False
        self.isFolded = False
        self.streetBet = 0
        self.totalBet = 0

    #Resets the hero's state for a new round 
    def resetNewStreet(self):
        self.streetBet = 0
        self.isAllIn = False
        self.isFolded = False

    def isEliminated(self):
        return self.stack <= 0

    #Places the hero's bet into the pot and updates their stack and bet amounts
    def placedInPot(self, amount: int):
        amount = min(amount, self.stack) #If the hero doesn't have enough chips to call, they go all in
        self.stack -= amount
        self.Bet += amount
        self.totalBet += amount
        if self.stack <= 0:
            self.isAllIn = True
        return amount

    #Hero's info 
    def __repr__(self):
        return f"Hero(name={self.name}, stack={self.stack}, holeCards={self.holeCards}, position={self.position}, isAllIn={self.isAllIn}, isFolded={self.isFolded}, Bet={self.Bet}, totalBet={self.totalBet})"