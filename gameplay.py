import random
from collections import deque
from tableSetUp import smallBlind, bigBlind, preflop, postflop, betSize
from evals import newDeck, bestScore, handCategories
from hero import Hero
from decisions import preflopAction, postflopAction
from humanUI import getHumanAction


class Table:
    numPlayers = 6

    def __init__(self, startingStack: int = 1000, humanSeat: int = None):
        self.players = [Hero(f"Player {i + 1}", startingStack) for i in range(self.numPlayers)]
        if humanSeat is not None:
            self.players[humanSeat].isHuman = True
        self.buttonIndex = 0
        self.handNumber = 0
        self.board = []

    # Position relative to the button, so as the button rotates seat 0 might be LJ one hand and BTN a few hands later
    def assignPositions(self):
        offsets = {"BTN": 0, "SB": 1, "BB": 2, "LJ": 3, "HJ": 4, "CO": 5}
        for position, offset in offsets.items():
            seat = (self.buttonIndex + offset) % self.numPlayers
            self.players[seat].position = position

    def playerAt(self, position: str) -> Hero:
        return next(p for p in self.players if p.position == position)

    def numLivePlayers(self) -> int:
        return sum(1 for p in self.players if not p.folded)

    # Sum of every player's current stack. Used to verify no chips are created/destroyed between hands.
    def totalChips(self) -> int:
        return sum(p.stack for p in self.players)

    def playHand(self) -> dict:
        if any(p.isEliminated() for p in self.players):  # This engine only handles a full 6-handed table
            return None

        self.handNumber += 1
        for p in self.players:
            p.resetForNewHand()
        self.assignPositions()
        deck = newDeck()
        random.shuffle(deck)
        for p in self.players:
            p.holeCards = [deck.pop(), deck.pop()]

        # Post the blinds
        self.playerAt("SB").putInPot(smallBlind)
        self.playerAt("BB").putInPot(bigBlind)

        self.board = []
        self.bettingRound(preflop, isPreFlop=True)

        for streetCards in (3, 1, 1):  # Flop (3 cards), then turn and river (1 each)
            if self.numLivePlayers() <= 1:
                break
            for p in self.players:
                p.resetForNewStreet()
            self.board += [deck.pop() for _ in range(streetCards)]
            self.bettingRound(postflop, isPreFlop=False)

        result = self.resolveHand()
        self.buttonIndex = (self.buttonIndex + 1) % self.numPlayers
        return result

    # Determine the order of players for this betting round
    def bettingRound(self, positionOrder: list, isPreFlop: bool):
        orderedPlayers = sorted(
            (p for p in self.players if not p.folded and not p.allIn),
            key=lambda p: positionOrder.index(p.position)
        )
        queue = deque(orderedPlayers)
        currentBet = max(p.currentBet for p in self.players)

        while queue:
            player = queue.popleft()
            if player.folded or player.allIn:
                continue

            if self.numLivePlayers() <= 1:
                return  # If only one player remains, end the betting round

            pot = sum(p.totalCommitted for p in self.players)  # Current pot size
            toCall = currentBet - player.currentBet
            facingBet = toCall > 0
            betAmount = max(bigBlind, int(pot * betSize))  # Bet size is either the big blind or a % of the pot

            if player.isHuman:
                action = getHumanAction(player, self.board, toCall, pot, betAmount, isPreFlop)
            elif isPreFlop:
                action = preflopAction(player.position, player.holeCards, facingBet)
            else:
                action = postflopAction(player.holeCards, self.board, facingBet)

            if action == "fold":
                if facingBet:
                    player.folded = True
            elif action == "call":
                if facingBet:
                    player.putInPot(toCall)
            elif action == "check":
                if facingBet:
                    raise ValueError("Cannot check when facing a bet.")
            elif action in ("bet", "raise"):
                player.putInPot(toCall + betAmount)
                currentBet = player.currentBet
                # Re-add other live players so they can respond to the new bet/raise
                queue.extend(p for p in self.players if not p.folded and not p.allIn and p != player)

            queue = deque(p for p in queue if not p.folded and not p.allIn)

    # Complete the hand and determine the winner(s)
    def resolveHand(self) -> dict:
        pot = sum(p.totalCommitted for p in self.players)
        livePlayers = [p for p in self.players if not p.folded]

        if len(livePlayers) == 1:
            winner = livePlayers[0]
            winner.stack += pot
            return {
                "handNumber": self.handNumber,
                "winners": [winner.name],
                "pot": pot,
                "showdown": False,
                "winningHand": None,
                "board": [str(c) for c in self.board],
            }

        # Evaluate hands for all live players
        playerScores = {p: bestScore(p.holeCards + self.board) for p in livePlayers}
        bestScoreValue = max(playerScores.values())
        winners = [p for p, score in playerScores.items() if score == bestScoreValue]

        # Split the pot evenly; any odd remainder goes to the first winner
        share = pot // len(winners)
        for w in winners:
            w.stack += share
        remainder = pot - share * len(winners)
        if remainder:
            winners[0].stack += remainder

        return {
            "handNumber": self.handNumber,
            "winners": [w.name for w in winners],
            "pot": pot,
            "showdown": True,
            "winningHand": handCategories[bestScoreValue[0]],
            "board": [str(c) for c in self.board],
        }