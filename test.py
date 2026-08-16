#Tests for the poker project. Run with: pytest test_poker.py
import random
from evals import Card, Rank, Suit, parseCard, newDeck, scoreFive, bestScore, handCategories
from decisions import (handScore, allScores, cutOff, preflopAction, postflopAction, bestFiveCards, 
                       rangeFromTopPercent, expandHandTypes, handVsRangeEquity, evFold, evCall, 
                       evRaise, decisionEV)
from hero import Hero
from gameplay import Table


def cards(spec): #eg cards("Ah Kd Qc") -> [Card, Card, Card]
    return [parseCard(c) for c in spec.split()]


#Tests for evals
def test_new_deck_has_52_unique_cards():
    deck = newDeck()
    assert len(deck) == 52
    assert len(set(deck)) == 52 #needs Card to be hashable

def test_parse_card_round_trips():
    c = parseCard("Ah")
    assert c.rank == Rank.ACE and c.suit == Suit.HEARTS
    assert str(c) == "Ah"

def test_royal_flush_is_straight_flush():
    category = scoreFive(cards("Ah Kh Qh Jh Th"))[0]
    assert handCategories[category] == "Straight Flush"

def test_wheel_straight_ace_low():
    category, highCard = scoreFive(cards("Ah 2d 3c 4s 5h"))
    assert handCategories[category] == "Straight"
    assert highCard == 5 #the 5, not the ace, is high card of a wheel

def test_full_house():
    category = scoreFive(cards("Ah Ad Ac Kh Kd"))[0]
    assert handCategories[category] == "Full House"

def test_two_pair():
    category = scoreFive(cards("Ah Ad Kc Ks 2d"))[0]
    assert handCategories[category] == "Two Pair"

def test_hand_category_ordering():
    highCard = scoreFive(cards("Ah Kd Qc 9s 2d"))
    onePair = scoreFive(cards("7h 7d Kc Qs 2d"))
    twoPair = scoreFive(cards("5h 5d 6c 6s 2d"))
    trips = scoreFive(cards("4h 4d 4c Kh 2d"))
    straight = scoreFive(cards("9h 8d 7c 6s 5h"))
    flush = scoreFive(cards("Ah 9h 7h 4h 2h"))
    fullHouse = scoreFive(cards("3h 3d 3c Kh Kd"))
    fourKind = scoreFive(cards("2h 2d 2c 2s Kh"))
    straightFlush = scoreFive(cards("Ah Kh Qh Jh Th"))
    ordered = [highCard, onePair, twoPair, trips, straight, flush, fullHouse, fourKind, straightFlush]
    assert ordered == sorted(ordered) #each one beats the last

def test_kicker_breaks_ties():
    bigKicker = scoreFive(cards("Ah Ad Kc Qs 2d"))
    smallKicker = scoreFive(cards("Ah Ad 9c 5s 2d"))
    assert bigKicker > smallKicker

def test_best_score_finds_a_straight_over_trips():
    #7 cards contain trip aces AND a wheel straight - the straight should win
    sevenCards = cards("Ah Ad Ac 2d 3c 4s 5h")
    category = bestScore(sevenCards)[0]
    assert handCategories[category] == "Straight"


#Tests for decisions
def test_pocket_aces_scores_20_known_chen_value():
    assert handScore(14, 14, False) == 20 # Chen value for AA

def test_suited_beats_offsuit_same_ranks():
    assert handScore(14, 13, True) > handScore(14, 13, False)

def test_all_starting_hand_types_present():
    assert len(allScores) == 169 #13 pairs + 78 suited + 78 offsuit

def test_cutoffs_tighter_in_earlier_position():
    assert cutOff["LJ"] >= cutOff["BTN"] #LJ acts first, needs a stronger hand

def test_preflop_folds_worst_hand():
    assert preflopAction("LJ", cards("7c 2d"), facingBet=False) == "fold"

def test_preflop_raises_best_hand():
    assert preflopAction("LJ", cards("Ah Ad"), facingBet=False) == "raise"

def test_postflop_raises_a_set():
    board = cards("Ac 2d 3s")
    assert postflopAction(cards("Ah Ad"), board, facingBet=False) == "raise"

def test_postflop_folds_air_facing_a_bet():
    board = cards("Ah Kd Qs")
    assert postflopAction(cards("7c 2d"), board, facingBet=True) == "fold"

def test_best_five_cards_returns_five():
    holeCards = cards("Ah Ad")
    board = cards("Ac 2d 3s 4c 5h")
    assert len(bestFiveCards(holeCards + board)) == 5


#Tests for decisions EV and equity
def test_range_from_top_percent_length():
    assert len(rangeFromTopPercent(0.1)) == round(0.1 * 169)

def test_expand_hand_types_combo_counts():
    pair = expandHandTypes([(Rank.ACE, Rank.ACE, False)], deadCards=[])
    suited = expandHandTypes([(Rank.ACE, Rank.KING, True)], deadCards=[])
    offsuit = expandHandTypes([(Rank.ACE, Rank.KING, False)], deadCards=[])
    assert len(pair) == 6 and len(suited) == 4 and len(offsuit) == 12

def test_expand_hand_types_excludes_dead_cards():
    pair = expandHandTypes([(Rank.ACE, Rank.ACE, False)], deadCards=cards("Ah"))
    assert len(pair) == 3 #only the 3 remaining aces can still pair up

def test_premium_hand_has_high_equity_on_dry_board():
    random.seed(0)
    hero = cards("Ah Ad")
    board = cards("7c 2d 9s")
    result = handVsRangeEquity(hero, rangeFromTopPercent(0.3), board, numSimulations=2000)
    assert result["win"] + result["tie"] / 2 > 0.7

def test_weak_hand_has_low_equity_on_scary_board():
    random.seed(0)
    hero = cards("7c 2d")
    board = cards("Ah Kd Qs")
    result = handVsRangeEquity(hero, rangeFromTopPercent(0.15), board, numSimulations=2000)
    assert result["win"] + result["tie"] / 2 < 0.2

def test_ev_fold_is_always_zero():
    assert evFold() == 0.0

def test_ev_call_matches_pot_odds_breakeven():
    pot, toCall = 100, 50
    breakeven = toCall / (pot + toCall)
    assert abs(evCall(breakeven, pot, toCall)) < 1e-9

def test_ev_call_sign_follows_equity_vs_pot_odds():
    assert evCall(equity=0.6, pot=100, toCall=50) > 0
    assert evCall(equity=0.1, pot=100, toCall=50) < 0

def test_ev_raise_improves_with_fold_equity_on_a_weak_hand():
    lowFoldEquity = evRaise(equity=0.1, pot=100, toCall=0, raiseSize=50, foldEquity=0.1)
    highFoldEquity = evRaise(equity=0.1, pot=100, toCall=0, raiseSize=50, foldEquity=0.8)
    assert highFoldEquity > lowFoldEquity

def test_decision_ev_recommends_fold_with_terrible_equity():
    random.seed(0)
    hero = cards("7c 2d")
    board = cards("Ah Kd Qs")
    result = decisionEV(hero, rangeFromTopPercent(0.15), board, pot=100, toCall=80,
                         raiseSize=200, foldEquity=0.1, numSimulations=2000)
    assert result["recommended"] == "fold"

def test_decision_ev_recommends_aggression_with_premium_equity():
    random.seed(0)
    hero = cards("Ah Ad")
    board = cards("7c 2d 9s")
    result = decisionEV(hero, rangeFromTopPercent(0.3), board, pot=100, toCall=50,
                         raiseSize=150, foldEquity=0.4, numSimulations=2000)
    assert result["recommended"] in ("call", "raise")


#Tests for hero
def test_new_hero_defaults_to_not_human():
    assert Hero("Bot", 1000).isHuman is False

def test_put_in_pot_moves_chips():
    h = Hero("Bot", 1000)
    h.putInPot(100)
    assert h.stack == 900 and h.currentBet == 100 and h.totalCommitted == 100

def test_going_all_in_caps_at_remaining_stack():
    h = Hero("Bot", 100)
    paid = h.putInPot(500)
    assert paid == 100 and h.stack == 0 and h.allIn is True

def test_folded_and_all_in_persist_across_streets():
    h = Hero("Bot", 1000)
    h.folded, h.allIn = True, True
    h.resetForNewStreet()
    assert h.folded is True and h.allIn is True #must not clear mid-hand

def test_reset_for_new_hand_clears_everything():
    h = Hero("Bot", 1000)
    h.putInPot(200)
    h.folded = True
    h.resetForNewHand()
    assert h.folded is False and h.totalCommitted == 0 and h.holeCards == []


#Tests for gameplay
def test_single_hand_conserves_chips():
    random.seed(1)
    table = Table(startingStack=1000, humanSeat=None)
    expected = table.numPlayers * 1000
    assert table.playHand() is not None
    assert table.totalChips() == expected

def test_showdown_winner_gets_paid():
    random.seed(2)
    table = Table(startingStack=1000, humanSeat=None)
    before = {p.name: p.stack for p in table.players}
    table.playHand()
    after = {p.name: p.stack for p in table.players}
    assert any(after[n] != before[n] for n in before)

def test_result_dict_always_has_showdown_key():
    random.seed(3)
    table = Table(startingStack=1000, humanSeat=None)
    for _ in range(20):
        result = table.playHand()
        if result is None:
            break
        assert "showdown" in result and isinstance(result["winners"], list)

def test_many_hands_never_break_chip_conservation():
    for seed in range(5):
        random.seed(seed)
        table = Table(startingStack=1000, humanSeat=None)
        expected = table.numPlayers * 1000
        for _ in range(50):
            result = table.playHand()
            if result is None: #someone busted, engine stops
                break
            assert table.totalChips() == expected