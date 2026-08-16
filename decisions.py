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