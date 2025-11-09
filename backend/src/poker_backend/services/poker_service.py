from math import inf
from pokerkit import Automation, NoLimitTexasHoldem


class PokerSimulationService:
    @staticmethod
    def simulate_hand(data: dict):
        """
        Executes a full sequence of poker actions using PokerKit (6-player Texas Hold'em).
        """
        # --- Extract input data ---
        antes = data.get("antes", 0)
        blinds = tuple(data.get("blinds", (20, 40)))  # (SB, BB)
        min_bet = data.get("min_bet", 40)
        stacks = data.get("stacks", [])
        players = data.get("players", [])
        actions = data.get("actions", [])
        min_raise = None

        # --- Ensure exactly 6 players ---
        while len(players) < 6:
            players.append("????")
        while len(stacks) < 6:
            stacks.append(50000)

        stacks_tuple = tuple(inf if s == "inf" else s for s in stacks)

        # --- Create a 6-player PokerKit state ---
        state = NoLimitTexasHoldem.create_state(
            (
                Automation.ANTE_POSTING,
                Automation.BET_COLLECTION,
                Automation.BLIND_OR_STRADDLE_POSTING,
                Automation.CARD_BURNING,
                # Removed: Automation.HOLE_CARDS_SHOWING_OR_MUCKING (manual showdown)
                Automation.HAND_KILLING,
                Automation.CHIPS_PUSHING,
                Automation.CHIPS_PULLING,
            ),
            False,              # no uniform antes
            antes,
            blinds,
            min_bet,
            stacks_tuple,
            6,
        )

        # --- Deal hole cards to all 6 players ---
        hole_cards = []
        for i in range(6):
            if i < len(players) and isinstance(players[i], list) and len(players[i]) == 2:
                # Player has specified hole cards
                cards = players[i]
            else:
                # Auto-generate random cards from remaining deck
                dealable = list(state.get_dealable_cards())
                if len(dealable) >= 2:
                    cards = [str(dealable[0]), str(dealable[1])]
                else:
                    cards = ["??", "??"]
            hole_cards.append(cards)
            try:
                state.deal_hole(cards)
            except Exception as e:
                print(f"⚠️ Warning: could not deal {cards} to player {i}: {e}")


        # --- Play through all actions ---
        for idx, a in enumerate(actions):
            print(f"\n🟩 ACTION {idx+1}: {a}")
            try:
                # --- Board dealing (flop / turn / river) ---
                if "deal_board" in a:
                    # Skip if there's still an active player who needs to act
                    if hasattr(state, 'actor_index') and state.actor_index is not None:
                        print(f"⚠️ Cannot deal board - player {state.actor_index} still needs to act")
                        continue
                    
                    # First, close the current betting round by collecting bets
                    while state.can_collect_bets():
                        state.collect_bets()
                        print("✅ Collected bets before dealing board")

                    # Burn and deal board
                    if state.can_burn_card():
                        state.burn_card()
                        print("🔥 Burned a card")

                    if state.can_deal_board():
                        state.deal_board(a["deal_board"])
                        print(f"✅ Dealt board: {a['deal_board']}")
                    else:
                        print("⚠️ Cannot deal board - not ready yet")
                    continue

                # --- Player actions ---
                t = a.get("type")
                
                # Skip action if no player to act (betting round already closed)
                if not hasattr(state, 'actor_index') or state.actor_index is None:
                    print("⚠️ No active player - betting round closed, skipping action")
                    continue

                if t == "fold":
                    state.fold()
                    print("🧍 Player folded")

                elif t in ("call", "check"):
                    state.check_or_call()
                    print("🧍 Player checked/called")
                    
                    # Auto-collect bets if betting round is complete
                    if state.can_collect_bets():
                        state.collect_bets()
                        print("✅ Auto-collected bets (round complete)")

                elif t in ("raise", "bet"):
                    amt = a.get("amount")
                    if amt is None:
                        print("⚠️ No amount specified for bet/raise")
                        continue
                    
                    state.complete_bet_or_raise_to(amt)
                    print(f"🧍 Player bet/raised to {amt}")

                elif t == "allin":
                    # Get current player's remaining stack
                    if hasattr(state, 'actor_index') and state.actor_index is not None:
                        current_stack = state.stacks[state.actor_index]
                        state.complete_bet_or_raise_to(current_stack)
                        print(f"🧍 Player went all-in with {current_stack}")

                elif t == "show":
                    # Only try to show if we're in showdown phase
                    if state.can_show_or_muck_hole_cards():
                        state.show_or_muck_hole_cards(True)
                        print("🧍 Player showed cards")
                    else:
                        print("⚠️ Not in showdown phase yet")

                else:
                    print(f"⚠️ Unknown action type: {t}")

                # --- Debug info ---
                print(f"🏆 Stacks: {state.stacks}")
                print(f"📍 Street: {state.street_index}")
                if hasattr(state, 'actor_index') and state.actor_index is not None:
                    print(f"👤 Current actor: {state.actor_index}")

            except Exception as e:
                print(f"❌ ERROR during action {idx+1} {a}: {e}")
                import traceback
                traceback.print_exc()

        # --- Final settlement ---
        try:
            # Collect any remaining bets
            while state.can_collect_bets():
                state.collect_bets()
                print("✅ Final bet collection")

            # Manual showdown for remaining players with known cards
            max_attempts = 10
            attempts = 0
            while state.can_show_or_muck_hole_cards() and attempts < max_attempts:
                try:
                    # Check if current player has known cards (not ????)
                    if hasattr(state, 'actor_index') and state.actor_index is not None:
                        player_cards = players[state.actor_index]
                        if player_cards != "????":
                            state.show_or_muck_hole_cards(True)
                            print(f"🃏 Player {state.actor_index} showed cards at showdown")
                        else:
                            # Muck unknown cards
                            state.show_or_muck_hole_cards(False)
                            print(f"🃏 Player {state.actor_index} mucked cards")
                    else:
                        break
                    attempts += 1
                except Exception as e:
                    print(f"⚠️ Showdown error: {e}")
                    break
            
            print(f"✅ Hand complete! Final stacks: {state.stacks}")
            print(f"✅ Payoffs: {state.payoffs if hasattr(state, 'payoffs') else 'N/A'}")
            
        except Exception as e:
            print(f"⚠️ Final settlement error: {e}")
            import traceback
            traceback.print_exc()
        try:
            if hasattr(state, "minimum_completion_bet_or_raise_to"):
                    min_raise = state.minimum_completion_bet_or_raise_to
                    print(f"💰 Minimum next raise: {min_raise}")
        except Exception as e:
                print(f"⚠️ Could not determine min_raise: {e}")  

                # --- Determine current actor and winner (if hand is complete) ---
        actor_index = getattr(state, "actor_index", None)
        winner_index = None
        try:
            if hasattr(state, "payoffs") and state.payoffs:
                max_payoff = max(state.payoffs)
                if max_payoff > 0:
                    winner_index = state.payoffs.index(max_payoff)
        except Exception:
            pass

   

        # --- Return final state snapshot ---
        return {
            "status":"complete",
            "players": [" ".join(cards) for cards in hole_cards],
            "winner_index": winner_index,
            "actions": actions,
            "min_raise": min_raise,
            "board": list(state.board_cards) if hasattr(state, 'board_cards') else [],
            "stacks": [float(s) if s != inf else "inf" for s in state.stacks],
            "engine_status": str(state.status) if hasattr(state, 'status') else "unknown",
            "payoffs": list(state.payoffs) if hasattr(state, 'payoffs') else [0] * 6,
            "final_pots": state.total_pot_amount if hasattr(state, 'total_pot_amount') else 0
        }