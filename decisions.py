from itertools import combinations
import random
from evals import Rank, Suit, Card, scoreFive, bestScore, newDeck

ranksAscending = sorted(Rank, key=lambda x: x.value)

#Chen formula for hand strength evaluation
def handScore(rank1: int, rank2:int, suited: bool)-> float:
    values = {14: 10, 13: 8, 12: 7, 11: 6,
            10: 5, 9: 4.5, 8: 4, 7: 3.5,
            6: 3, 5: 2.5, 4: 2, 3: 1.5, 2:1}
    high, low = max(rank1, rank2), min(rank1, rank2)
    score = values.get(high, high/2) #Base score is determined by the higher card in the hand
    if high == low: #Pair
        score = max(score*2, 5) #Pairs are worth double their high card value, but at least 5
    else: #Non-pair hands
        if suited:
            score += 2 
        if low != high: #The larger gaps being less favorable
            gap = (high - low) - 1
            if gap == 1:
                score -= 1
            elif gap == 2:
                score -= 2
            elif gap == 3:
                score -= 4
            elif gap >= 4:
                score -= 5
        if high < 12 and gap <= 1: #Bonus for low connected cards
            score += 1
    return round(score)

def startingHandScores()-> list:
    startingHands = []
    for i in range(len(ranksAscending)):
        for j in range(i, len(ranksAscending)):
            rank1, rank2 = ranksAscending[i], ranksAscending[j]
            score = handScore(rank1.value, rank2.value, False) #Default to offsuit
            startingHands.append((rank1, rank2, False, score))
            if rank1.value != rank2.value: #If the two cards are the same rank, they cannot be suited
                score = handScore(rank1.value, rank2.value, True)
                startingHands.append((rank1, rank2, True, score))
    return sorted(startingHands, key=lambda x: x[3], reverse=True)

#Cheat sheet of all possible starting hands and their scores (descending order)
def startingHadsLabeled()-> list:
    from evals import rankChar
    startingHands = []
    for i in range(len(ranksAscending)):
        for j in range(i, len(ranksAscending)):
            rank1, rank2 = ranksAscending[i], ranksAscending[j]
            score = handScore(rank1.value, rank2.value, False) #Default to offsuit
            label = rankChar[rank1] + rankChar[rank2] + "o"
            startingHands.append((label, score))
            if rank1.value != rank2.value: #If the two cards are the same rank, they cannot be suited
                score = handScore(rank1.value, rank2.value, True)
                label = rankChar[rank1] + rankChar[rank2] + "s"
                startingHands.append((label, score))
    return sorted(startingHands, key=lambda x: x[1], reverse=True)

allScores = startingHandScores() #List of all possible starting hands and their scores(descending order)

preFlopRaise = {"LJ": 0.17, "HJ": 0.22, "CO": 0.293, "BTN": 0.481, "SB": 0.472, "BB": 0.436} #Percentage of starting hands that should be raised from each position
#https://blog.freebetrange.com/article/preflop-charts-open-raise-in-6-max-poker-cash-games

def scoreCutoff(positions:str) -> float:
    pct = preFlopRaise[positions]
    index = max(0, min(len(allScores)-1, round(pct*len(allScores))-1)) #Ensures the index is within the bounds of the list
    return allScores[index][3] #Returns the score of the hand at the cutoff index

cutOff = {pos: scoreCutoff(pos) for pos in preFlopRaise} #Dictionary of the score cutoffs for each position 

#Preflop decision making based on the hero's position, hole cards, and whether they are facing a bet
def preflopAction(pos:str, holeCards: list, facingBet: bool) -> str:
    rank1, rank2 = holeCards[0].rank.value, holeCards[1].rank.value
    suited = holeCards[0].suit == holeCards[1].suit
    score = handScore(rank1, rank2, suited)
    makeABet = score >= cutOff[pos] #If the hand's score is above the cutoff for the position, raise
    if not makeABet:
        return "fold"
    return "call" if facingBet else "raise" #If facing a bet, call, otherwise raise

#Postflop decision making based on the hero's hole cards, community cards, and whether they are facing a bet
def postflopAction(holeCards: list, communityCards: list, facingBet: bool) -> str:
    allCards = holeCards + communityCards
    score = bestScore(allCards)[0] #Get the best 5 card hand from the hero's hole cards and the community cards
    if facingBet:
        if score >= 3: #Three of a kind or better
            return "raise"
        elif score == 2: #Two pair
            return "call"
        elif score == 1: #One pair
            return "call"
        else: #High card
            return "fold"
    else:
        if score >= 3: #Three of a kind or better
            return "bet"
        elif score == 2: #Two pair
            return "bet"
        elif score == 1: #One pair
            return "check"
        else: #High card
            return "check"

#Finds the best 5 card hand from a list of cards and returns it
def bestFiveCards(cards: list) -> list:
    best = []
    bestScoreValue = (0, [])
    for combo in combinations(cards, 5):
        score = scoreFive(list(combo))
        if score > bestScoreValue:
            bestScoreValue = score
            best = list(combo)
    return best

#Returns the (rank1, rank2, suited) hand types making up the top pct of allScores
#eg rangeFromTopPercent(0.2) = the top 20% of starting hands
def rangeFromTopPercent(pct: float) -> list:
    n = max(1, round(pct * len(allScores)))
    return [(r1, r2, suited) for (r1, r2, suited, score) in allScores[:n]]

def expandHandTypes(handTypes: list, deadCards: list) -> list:
    dead = set(deadCards) #
    combos = []
    for r1, r2, suited in handTypes:
        if r1 == r2: #Pocket pair: any 2 of the 4 suits (6 combos)
            suits = list(Suit)
            for i in range(len(suits)):
                for j in range(i + 1, len(suits)):
                    c1, c2 = Card(r1, suits[i]), Card(r2, suits[j])
                    if c1 not in dead and c2 not in dead:
                        combos.append((c1, c2))
        elif suited: #Same suit (4 combos)
            for s in Suit:
                c1, c2 = Card(r1, s), Card(r2, s)
                if c1 not in dead and c2 not in dead:
                    combos.append((c1, c2))
        else: #Offsuit: different ranks and different suits (12 combos)
            for s1 in Suit:
                for s2 in Suit:
                    if s1 != s2:
                        c1, c2 = Card(r1, s1), Card(r2, s2)
                        if c1 not in dead and c2 not in dead:
                            combos.append((c1, c2))
    return combos

#Monte Carlo win/tie/lose probability for hero against a whole range of possible villain hands, given the known board 
def handVsRangeEquity(heroCards: list, villainHandTypes: list, board: list, numSimulations: int = 3000) -> dict:
    deadCards = heroCards + board
    combos = expandHandTypes(villainHandTypes, deadCards)
    if not combos:
        raise ValueError("No combos left in villain's range given the known cards.")

    dead = set(deadCards)
    wins, ties, losses = 0, 0, 0
    for _ in range(numSimulations):
        villainCards = list(random.choice(combos))
        deck = [c for c in newDeck() if c not in dead and c not in villainCards]
        random.shuffle(deck)

        currentBoard = board.copy()
        while len(currentBoard) < 5:
            currentBoard.append(deck.pop())

        heroScore = bestScore(heroCards + currentBoard)
        villainScore = bestScore(villainCards + currentBoard)
        if heroScore > villainScore:
            wins += 1
        elif villainScore > heroScore:
            losses += 1
        else:
            ties += 1

    total = wins + ties + losses
    return {"win": wins / total, "tie": ties / total, "lose": losses / total}

#pot = chips already in the middle before hero acts (not including toCall)
#toCall = extra chips needed just to match the current bet
#equity = P(win) + P(tie)/2, the standard way to collapse win/tie/lose into one number

#Folding never does anything further
def evFold() -> float:
    return 0.0

#EV(call) = equity x finalPot - toCall, where finalPot = pot + toCall
#Pot-odds break-even check written as an EV: calling is +EV whenever equity > toCall / (pot + toCall)
def evCall(equity: float, pot: float, toCall: float) -> float:
    finalPot = pot + toCall
    return equity * finalPot - toCall

#EV(raise) = foldEquity x (what you win if villain folds) + (1-foldEquity) x (showdown EV)
#foldEquity (chance villain folds to the raise) is a genuine unknown you have to estimate - the formula is only as good as this input
def evRaise(equity: float, pot: float, toCall: float, raiseSize: float, foldEquity: float) -> float:
    if pot < 0 or toCall < 0 or raiseSize < 0:
        raise ValueError("Pot and action sizes cannot be negative.")
    if not 0 <= equity <= 1:
        raise ValueError("Equity must be between 0 and 1.")
    if not 0 <= foldEquity <= 1:
        raise ValueError("Fold equity must be between 0 and 1.")

    # Hero calls the existing bet and raises 
    raiseCost = toCall + raiseSize
    # If called, villain contributes  more.
    finalPotIfCalled = pot + toCall + 2 * raiseSize
    # If villain folds, hero's incremental profit is the pot that existed before hero acted. Hero's own contribution is not profit.
    foldBranchEV = pot

    calledBranchEV = (
        equity * finalPotIfCalled
        - raiseCost
    )
    return (
        foldEquity * foldBranchEV
        + (1 - foldEquity) * calledBranchEV
    )

#Runs the range equity calc and returns the EV of every action available (fold is only meaningful when facing a bet), plus which one has the highest EV
def decisionEV(heroCards: list, villainHandTypes: list, board: list, pot: float, toCall: float,
               raiseSize: float, foldEquity: float = 0.4, numSimulations: int = 3000) -> dict:
    result = handVsRangeEquity(heroCards, villainHandTypes, board, numSimulations)
    equity = result["win"] + result["tie"] / 2

    evs = {"equity": equity, **result}
    evs["fold"] = evFold() if toCall > 0 else None
    evs["call"] = evCall(equity, pot, toCall) if toCall > 0 else None
    evs["raise"] = evRaise(equity, pot, toCall, raiseSize, foldEquity)

    candidates = {k: v for k, v in evs.items() if k in ("fold", "call", "raise") and v is not None}
    evs["recommended"] = max(candidates, key=candidates.get)
    return evs