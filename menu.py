from gameplay import Table
from tableSetUp import startingStack
from evals import parseCard
from humanUI import showHandRankings, printCheatSheet, calcOdds
from equity import rangeFromTopPercent, decisionEV

def printHandResult(result: dict):
    if result["showdown"]:
        board = " ".join(result["board"])
        winners = " & ".join(result["winners"])
        print(f"\nHand #{result['handNumber']} result: board [{board}]")
        print(f"{winners} won {result['pot']} chips with {result['winningHand']}")
    else:
        winner = result["winners"][0]
        print(f"\nHand #{result['handNumber']} result: everyone else folded")
        print(f"{winner} won {result['pot']} chips")

def runSession(numHands: int, humanSeat: int = None, verbose: bool = True):
    table = Table(startingStack=startingStack, humanSeat=humanSeat)
    expectedTotalChips = table.numPlayers * startingStack
    handsPlayed = 0

    for _ in range(numHands):
        result = table.playHand()
        if result is None:
            print("\nSomeone busted: need a full 6-handed table, stopping here.")
            break

        handsPlayed += 1
        if verbose:
            printHandResult(result)

        # Account for chips
        actual = table.totalChips()
        assert actual == expectedTotalChips, f"Chip count mismatch: expected {expectedTotalChips}, got {actual}"

        # Check if human player wants to continue
        if humanSeat is not None:
            again = input("\nPress Enter for the next hand, or type 'q' to stop: ").strip().lower()
            if again == "q":
                break

    print(f"\nSession summary after {handsPlayed} hands")
    for p in table.players:
        change = p.stack - startingStack
        sign = "+" if change >= 0 else ""
        tag = "  <- you" if p.isHuman else ""
        print(f"{p.name}: {p.stack} chips ({sign}{change}){tag}")

#Default function to run a session of 1000 hands with the human player in seat 0
def playYourself():
    showHandRankings()
    print("Your seat stays the same, but your position changes")
    print("each hand as the button rotates.\n")
    input("Press Enter when you're ready to start...")
    runSession(numHands=1000, humanSeat=0, verbose=True)

def watchComputers():
    raw = input("How many hands should the players play? (default 20): ").strip()
    numHands = int(raw) if raw else 20
    runSession(numHands=numHands, humanSeat=None, verbose=True)

def compareHands():
    try:
        hand1Str = input("Enter the first hand (e.g., 'Ah Kh'): ").strip()
        hand2Str = input("Enter the second hand (e.g., 'Qd Qc'): ").strip()
        hand1 = [parseCard(c) for c in hand1Str.split()]
        hand2 = [parseCard(c) for c in hand2Str.split()]
        result = calcOdds(hand1, hand2, board=[], numSimulations=10000)
        print(f"\nResults after 10,000 trials:")
        print(f"Hand 1 win percentage: {result['hand1_win_pct']}%")
        print(f"Hand 2 win percentage: {result['hand2_win_pct']}%")
        print(f"Tie percentage: {result['tie_pct']}%")
    except Exception as e:
        print(f"Error comparing hands: {e}")

def evAnalysis():
    try:
        heroStr = input("Your hand (e.g., 'Ah Ad'): ").strip()
        boardStr = input("Board so far (e.g., '7c 2d 9s', or leave blank preflop): ").strip()
        hero = [parseCard(c) for c in heroStr.split()]
        board = [parseCard(c) for c in boardStr.split()] if boardStr else []

        rangePct = float(input("Opponent's range as top % of hands (e.g. 20 for top 20%): ").strip() or 20) / 100
        villainRange = rangeFromTopPercent(rangePct)

        pot = float(input("Current pot size: ").strip())
        toCall = float(input("Amount you need to call (0 if no bet facing you): ").strip() or 0)
        raiseSize = float(input("Size of the raise/bet you're considering (on top of the call): ").strip())
        foldEquity = float(input("Estimated chance opponent folds to your raise, 0-1 (default 0.4): ").strip() or 0.4)

        result = decisionEV(hero, villainRange, board, pot, toCall, raiseSize, foldEquity, numSimulations=4000)

        print(f"\nEquity vs top {rangePct*100:.0f}% range: {result['equity']*100:.1f}% "
              f"(win {result['win']*100:.1f}% / tie {result['tie']*100:.1f}% / lose {result['lose']*100:.1f}%)")
        if result["fold"] is not None:
            print(f"EV(fold)  = {result['fold']:.1f}")
        if result["call"] is not None:
            print(f"EV(call)  = {result['call']:.1f}")
        print(f"EV(raise) = {result['raise']:.1f}")
        print(f"-> Highest-EV action: {result['recommended']}")
    except Exception as e:
        print(f"Error running EV analysis: {e}")

def main():
    print("Welcome to the Poker Mini Project!")
    while True:
        print("\nMenu:")
        print("1) Play yourself")
        print("2) Watch computer players")
        print("3) Compare two hands")
        print("4) Print cheat sheet")
        print("5) EV analysis vs an opponent range")
        print("6) Exit")
        choice = input("Choose an option: ").strip()
        if choice == "1":
            playYourself()
        elif choice == "2":
            watchComputers()
        elif choice == "3":
            compareHands()
        elif choice == "4":
            printCheatSheet()
        elif choice == "5":
            evAnalysis()
        elif choice == "6":
            print("Exiting the game.")
            break
        else:
            print("Invalid option. Please choose 1-6.")

if __name__ == "__main__":
    main()