from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from poker_backend.models.hand import Hand
from poker_backend.repositories.hand_repository import HandRepository
from poker_backend.services.poker_service import PokerSimulationService
from poker_backend.db.connection import get_connection
import ast


router = APIRouter(prefix="/hand", tags=["Hands"])

@router.post("/simulate")
def simulate_hand(data: Dict[str, Any]):
    try:
        result = PokerSimulationService.simulate_hand(data)
        return result
    except Exception as e:
        import traceback
        print("❌ Error during hand simulation:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/")
def save_hand(hand_data: Dict[str, Any], conn=Depends(get_connection)):
    repo = HandRepository(conn)

    players = hand_data.get("players", [])
    normalized_players = []

    # Normalize in case frontend sent stringified lists
    for p in players:
        if isinstance(p, str):
            try:
                parsed = ast.literal_eval(p)
                normalized_players.append(parsed)
            except Exception:
                normalized_players.append([p])
        else:
            normalized_players.append(p)

    hand = Hand(
        hand_id=None,
        players=normalized_players,
        actions=hand_data["actions"],
        board_cards=hand_data.get("board_cards", []),
        stacks=hand_data["stacks"],
        winner_index=hand_data.get("winner_index"),
    )
    saved = repo.save_hand(hand)
    return saved.__dict__


@router.get("/")
def get_all_hands(conn=Depends(get_connection)):
    repo = HandRepository(conn)
    return [h.__dict__ for h in repo.get_all_hands()]
