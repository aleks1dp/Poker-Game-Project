from evals import Rank, scoreFive, bestScore, handCategories, parseCard, newDeck
from decisions import handScore, cutOff, startingHadsLabeled
from itertools import combinations
import random

#https://pokertrainer.se/hand-ranking/
rankingBestToWorst = [
    "Straight Flush - any straight with all five cards of the same suit",
    "Four of a Kind - any four cards of the same rank",
    "Full House - three cards of one rank together with two cards of another rank",
    "Flush - five cards of the same suit (not consecutive)",
    "Straight - five consecutive cards (not all of the same suit)",
    "Three of a Kind - any three cards of the same rank",
    "Two Pair - two cards of one rank together with two cards of another rank",
    "One Pair - any two cards of the same rank",
    "High Card - any hand that does not match one of the above; the highest card wins",
]

positionTips = {
    "LJ": "LJ = 'Lowjack'. You act FIRST, before anyone else has shown what they'll do. Play it safe here - only strong hands.",
    "HJ": "HJ = 'Hijack'. Still fairly early, so keep your standards a bit tighter than the seats after you.",
    "CO": "CO = 'Cutoff'. One seat before the button - you can start playing more hands here.",
    "BTN": "BTN = 'Button'. The best seat at the table - you act LAST every round after the flop, so you get to see everyone else's move first.",
    "SB": "SB = 'Small Blind'. You're forced to bet a little before seeing your cards, and you act early after the flop - a tough spot.",
    "BB": "BB = 'Big Blind'. You're forced to bet more before seeing your cards, but you get to act last before the flop.",
}

def showHandRankings():
    print("\nPoker Hand Rankings (best to worst):")
    for i, description in enumerate(rankingBestToWorst):
        print(f"  {len(rankingBestToWorst) - i}. {description}")
    print()

def describeStartingHand(holeCards: list) -> str:
    rank1, rank2 = holeCards[0].rank.value, holeCards[1].rank.value
    suited = holeCards[0].suit == holeCards[1].suit
    score = handScore(rank1, rank2, suited)
    if score >= cutOff["LJ"]:
        return "Premium hand: strong enough to play from any seat"
    elif score >= cutOff["CO"]:
        return "Solid hand: worth playing from most seats"
    elif score >= cutOff["BTN"]:
        return "Marginal hand: only really worth it from a late seat like BTN"
    else:
        return "Weak hand: usually best to fold this one"   

def describeCurrentHand(holeCards: list, board: list) -> str:
    if not board:
        return None  # nothing to describe preflop, there's no hand yet
    allCards = holeCards + board
    best = max(combinations(allCards, 5), key=lambda combo: scoreFive(list(combo)))
    category, _ = scoreFive(list(best))
    return handCategories[category]

def printCheatSheet():
    hands = startingHadsLabeled()
    earlyCutoff = cutOff["LJ"]
    lateCutoff = cutOff["BTN"]

    print("\nStarting Hands Cheatsheet:")
    print(f"{len(hands)} hand types, ranked from strongest to weakest. The score cutoffs for early (strongest) and late (weaker) positions are:")
    print(f"  Early (LJ): {earlyCutoff}")
    print(f"  Late (BTN): {lateCutoff}")
    print("\nAnything weaker is usually a fold.\n")

def calcOdds(hand1: list, hand2: list, board: list, numSimulations: int = 2000) -> dict:
    wins1, wins2, ties = 0, 0, 0
    knownCards = hand1 + hand2 + board
    for _ in range(numSimulations):
        deck = newDeck()
        # Remove the known cards from the deck
        for card in knownCards:
            deck.remove(card)
        random.shuffle(deck)

        # Complete the board if necessary
        currentBoard = board.copy()
        while len(currentBoard) < 5:
            currentBoard.append(deck.pop())

        # bestScore evaluates the best 5-card hand out of the 7 cards available
        # (handScore is only for scoring a 2-card starting hand preflop, not a made hand)
        score1 = bestScore(hand1 + currentBoard)
        score2 = bestScore(hand2 + currentBoard)

        if score1 > score2:
            wins1 += 1
        elif score2 > score1:
            wins2 += 1
        else:
            ties += 1

    return {
        "hand1_win_pct": round(100 * wins1 / numSimulations, 1),
        "hand2_win_pct": round(100 * wins2 / numSimulations, 1),
        "tie_pct": round(100 * ties / numSimulations, 1),
    }

def getHumanAction(hero, board: list, toCall: int, pot: int, betAmount: int, isPreFlop: bool) -> str:

    print(f"\n--- {hero.name} ({hero.position}) ---")
    print(positionTips[hero.position])

    holeCards = " ".join(str(card) for card in hero.holeCards)

    if isPreFlop:
        handDesc = describeStartingHand(hero.holeCards)
        print(f"Your cards: {holeCards}")
        print(f"Hand strength: {handDesc}")

    else:
        boardCards = " ".join(str(card) for card in board)
        currentHand = describeCurrentHand(hero.holeCards, board)
        print(f"Your cards: {holeCards}")
        print(f"Board:      {boardCards}")
        print(f"Best hand:  {currentHand}")

    print(f"\nPot: {pot} chips")
    print(f"Stack: {hero.stack} chips")

    if toCall > 0:
        totalContribution = min(toCall + betAmount, hero.stack)
        print(f"\nYou need {toCall} chips to call.")
        print("1) Fold")
        print(f"2) Call {min(toCall, hero.stack)}")
        print(
            f"3) Call {toCall} and raise by {betAmount} "
            f"({totalContribution} chips contributed now)"
        )

        validActions = {
            "1": "fold",
            "2": "call",
            "3": "raise",
    }
    else:
        print("\nNo bet to call.")
        print("1) Check")
        print(f"2) Bet {betAmount}")
        validActions = {
            "1": "check",
            "2": "bet"
        }

    while True:
        choice = input("Choose an action: ").strip()
        if choice in validActions:
            return validActions[choice]
        print(
            "Invalid choice. Enter "
            + ", ".join(validActions.keys())
            + "."
        )