from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime

@dataclass
class Hand:
    hand_id: Optional[str]
    players: List[str]
    actions: List[Dict[str, Any]]
    board_cards: List[str]
    stacks: List[float]
    winner_index: Optional[int]
    created_at: Optional[datetime] = None
