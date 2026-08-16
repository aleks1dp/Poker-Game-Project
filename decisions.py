from itertools import combinations
import random
from evals import Rank, scoreFive

ranksAscending = sorted(Rank, key=lambda x: x.value)

#Chen formula for hand strength evaluation
def handScore(rank1: int, rank2:int, suited: bool)-> float:
    values = {14: 10, 13: 8, 12: 7, 11: 6,
            10: 5, 9: 4.5, 8: 4, 7: 3.5,
            6: 3, 5: 2.5, 4: 2, 3: 1.5, 2:1}
    high, low = max(rank1, rank2), min(rank1, rank2)
    score = values[high] #Base score is determined by the higher card in the hand
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

allScores = startingHandScores() #List of all possible starting hands and their scores(descending order)

preFlopRaise = {"LJ": 0.17, "HJ": 0.22, "CO": 0.293, "BTN": 0.481, "SB": 0.472, "BB": 0.436} #Percentage of starting hands that should be raised from each position
#https://blog.freebetrange.com/article/preflop-charts-open-raise-in-6-max-poker-cash-games

def scoreCutoff(positions:str) -> float:
    pct = preFlopRaise[positions]
    index = max(0, min(len(allScores)-1, round(pct*len(allScores))-1)) #Ensures the index is within the bounds of the list
    return allScores[index][3] #Returns the score of the hand at the cutoff index

cutOff = {pos: scoreCutoff(pos) for pos in preFlopRaise} #Dictionary of the score cutoffs for each position 

#Preflop decision making based on the hero's position, hole cards, and whether they are facing a bet
def preFlopDecision(pos:str, holeCards: list, facingBet: bool) -> str:
    rank1, rank2 = holeCards[0].rank.value, holeCards[1].rank.value
    suited = holeCards[0].suit == holeCards[1].suit
    score = handScore(rank1, rank2, suited)
    makeABet = score >= cutOff[pos] #If the hand's score is above the cutoff for the position, raise
    if not makeABet:
        return "fold"
    return "call" if facingBet else "raise" #If facing a bet, call, otherwise raise

#Postflop decision making based on the hero's hole cards, community cards, and whether they are facing a bet
def postFlopDecision(holeCards: list, communityCards: list, facingBet: bool) -> str:
    allCards = holeCards + communityCards
    bestHand = bestFiveCards(allCards) #Get the best 5 card hand from the hero's hole cards and the community cards
    score = scoreFive(bestHand)[0] #Get the hand category score (0-8)

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
            return "raise"
        elif score == 2: #Two pair
            return "raise"
        elif score == 1: #One pair
            return "call"
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
        