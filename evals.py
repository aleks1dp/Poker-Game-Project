from itertools import combinations
from collections import Counter
from dataclasses import dataclass
from enum import Enum

class Suit(Enum):
    HEARTS = 'h'
    DIAMONDS = 'd'
    CLUBS = 'c'
    SPADES = 's'

class Rank(Enum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14

rankChar =  {Rank.TWO: '2', Rank.THREE: '3', Rank.FOUR: '4', Rank.FIVE: '5', 
            Rank.SIX: '6', Rank.SEVEN: '7', Rank.EIGHT: '8', Rank.NINE: '9', 
            Rank.TEN: 'T', Rank.JACK: 'J', Rank.QUEEN: 'Q', Rank.KING: 'K', Rank.ACE: 'A'}

@dataclass
class Card:
    rank: Rank
    suit: Suit

    def __str__(self):
        return f"{rankChar[self.rank]}{self.suit.value}"

charToRank = {v: k for k, v in rankChar.items()}
charToSuit = {'h': Suit.HEARTS, 'd': Suit.DIAMONDS, 'c': Suit.CLUBS, 's': Suit.SPADES}

#Turns a string into Card object
def parseCard(text: str) -> Card:
    rankChar, suitChar = text[0].upper(), text[1].lower()
    return Card(charToRank[rankChar], charToSuit[suitChar])

def newDeck() -> list:
    return [Card(rank, suit) for suit in Suit for rank in Rank]

handCategories = {8: "Straight Flush", 7: "Four of a Kind", 6: "Full House", 5: "Flush",
                4: "Straight", 3: "Three of a Kind", 2: "Two Pair", 1: "One Pair", 0: "High Card"}

def scoreFive(cards: list) -> tuple:
    values = sorted([card.rank.value for card in cards], reverse=True) #Values sorted in descending order
    suits = [card.suit for card in cards] #Returns a list of the suits of the cards in the hand
    valueCounts = Counter(values) #Counts the occurrences of each value
    byCount = sorted(valueCounts.items(), key=lambda x: (-x[1], -x[0])) #Sorts by count first, then by value in descending order
    countPattern = [count for value, count in byCount] #Creates a list of the counts of each value

    isFlush = len(set(suits)) == 1 #Checks if all cards have the same suit
    uniqueValues = sorted(set(values), reverse=True) #Creates a list of the unique values in descending order
    isStraight, highCard = False, None #Checks if the cards form a straight and stores the high card if they do
    if len(uniqueValues) == 5: #If there are 5 unique values, check for a straight
        if uniqueValues[0] - uniqueValues[4] == 4: #Definition of a straight
            isStraight, highCard = True, uniqueValues[0]
        elif uniqueValues == [14, 5, 4, 3, 2]: #Ace low straight
            isStraight, highCard = True, 5

    if isStraight and isFlush: #Straight flush
        return (8, highCard)
    if countPattern[0] == 4: #Four of a kind
        return (7, [byCount[0][0], max([v for v in values if v != byCount[0][0]])]) #The kicker is the highest card that is not part of the four of a kind (second value in the tuple)
    if countPattern[0] == 3 and countPattern[1] == 2: #Full house
        return (6, byCount[0][0], byCount[1][0])
    if isFlush: 
        return (5, values)
    if isStraight:
        return (4, highCard)
    if countPattern[0] == 3: #Three of a kind
        return (3, [byCount[0][0]] + sorted([v for v in values if v != byCount[0][0]], reverse=True))
    if countPattern[0] == 2 and countPattern[1] == 2: #Two pair
        return (2, sorted([byCount[0][0], byCount[1][0]], reverse=True) + [v for v in values if v != byCount[0][0] and v != byCount[1][0]])
    if countPattern[0] == 2: #One pair
        return (1, [byCount[0][0]] + sorted([v for v in values if v != byCount[0][0]], reverse=True))
    return (0, values) #High card       

#Makes all combinations of 5 cards from the given list and returns the best score
def bestScore(cards: list) -> tuple: 
    best = (0, [])
    for combo in combinations(cards, 5):
        score = scoreFive(list(combo))
        if score > best:
            best = score
    return best