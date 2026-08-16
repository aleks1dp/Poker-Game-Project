Poker Game Priject

A six player Texas Hold'em simulator and decision analysis tool built using Python. The project combines poker hand evaluation, Monte Carlo simulation, opponent range modeling, and EV analysis.

The equity calculation simulates unknown community cards and samples an opponent holding from the selected range. Ties count as half a win:
equity = P(win) + 0.5 × P(tie)

The decision model then compares the incremental expected value of the actions. For example:
EV(call) = equity × (pot + call cost) - call cost


Inspiration

I was inspired to build this project after a trip to Las Vegas, where I played poker and finished about $50 ahead. The amount was small, but the experiencemade me curious about how much of each decision could be evaluated mathematically. 
I wanted to move beyond intuition and understand the underlying probability, risk, and expected value of folding, calling, or raising.


Features

- Simulates six-player Texas Hold'em with rotating positions and configurable human or computer-controlled players.
- Evaluates the best five-card hand from seven available cards, including all hand categories and tiebreakers.
- Estimates hand equity through Monte Carlo simulation.
- Models configurable opponent ranges using ranked starting-hand types.
- Compares fold, call, and raise decisions using pot odds, estimated equity, bet sizing, and fold probability.
- Tracks pots, player stacks, split pots, blinds, and chip conservation.
- Includes an interactive hand-comparison tool and starting-hand cheat sheet.


Project Structure

menu.py: command-line menu and session controls
gameplay.py: table state, betting rounds, dealing, and pot resolution
hero.py: player state and chip accounting
evals.py: card representation and poker-hand evaluation
decisions.py: strategy rules, opponent ranges, Monte Carlo equity, and EV
humanUI.py: interactive prompts and hand descriptions
tableSetUp.py: table and betting configuration
