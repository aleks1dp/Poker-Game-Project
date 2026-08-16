from gameplay import Table
from tableSetUp import startingStack
from humanUI import showHandRankings, printCheatSheet, calcOdds

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

    for _ in range(numHands): #Check if any player is eliminated
        result = table.playHand()
        if result is None:
            print("\nSomeone busted: need a full 6-handed table, stopping here.")
            break

        handsPlayed += 1
        if verbose:
            printHandResult(result)

        #Account for chips 
        actual = table.totalChips()
        assert actual == expectedTotalChips, f"Chip count mismatch: expected {expectedTotalChips}, got {actual}"

        #Check if human player wants to continue
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
        hand1 = input("Enter the first hand (e.g., 'Ah Kh'): ").strip()
        hand2 = input("Enter the second hand (e.g., 'Qd Qc'): ").strip()
        result = calcOdds(hand1, hand2, trials=10000)
        print(f"\nResults after 10,000 trials:")
        print(f"Hand 1 win percentage: {result['hand1_win_pct']}%")
        print(f"Hand 2 win percentage: {result['hand2_win_pct']}%")
        print(f"Tie percentage: {result['tie_pct']}%")
    except Exception as e:
        print(f"Error comparing hands: {e}")

def main():
    print("Welcome to the Poker Mini Project!")
    while True:
        print("\nMenu:")
        print("1) Play yourself")
        print("2) Watch computer players")
        print("3) Compare two hands")
        print("4) Print cheat sheet")
        print("5) Exit")
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
            print("Exiting the game.")
            break
        else:
            print("Invalid option. Please choose 1, 2, 3, or 4.")

if __name__ == "__main__":
    main()