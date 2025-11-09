import json
from typing import List
from psycopg import Connection
from poker_backend.models.hand import Hand

class HandRepository:
    def __init__(self, conn: Connection):
        self.conn = conn

    def create_table(self):
        with self.conn.cursor() as cur:
            cur.execute("""
            CREATE EXTENSION IF NOT EXISTS pgcrypto;
            CREATE TABLE IF NOT EXISTS hands (
                hand_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                players TEXT[] NOT NULL,
                actions JSONB NOT NULL,
                board_cards TEXT[] DEFAULT '{}',
                stacks NUMERIC[] DEFAULT '{}',
                winner_index INT,
                created_at TIMESTAMPTZ DEFAULT now()
            );
            """)
        self.conn.commit()

import json
from typing import List
from psycopg import Connection
from poker_backend.models.hand import Hand

class HandRepository:
    def __init__(self, conn: Connection):
        self.conn = conn

    def create_table(self):
        with self.conn.cursor() as cur:
            cur.execute("""
            CREATE EXTENSION IF NOT EXISTS pgcrypto;
            CREATE TABLE IF NOT EXISTS hands (
                hand_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                players TEXT[] NOT NULL,
                actions JSONB NOT NULL,
                board_cards TEXT[] DEFAULT '{}',
                stacks NUMERIC[] DEFAULT '{}',
                winner_index INT,
                created_at TIMESTAMPTZ DEFAULT now()
            );
            """)
        self.conn.commit()

    def save_hand(self, hand: Hand) -> Hand:
        # ✅ Normalize types
        players = hand.players
        if not players:
            players = []
        elif not isinstance(players, list):
            players = [str(players)]
        else:
            players = [str(p) for p in players]

        actions = hand.actions or []
        board_cards = hand.board_cards or []
        stacks = [float(s) for s in (hand.stacks or [])]
        winner_index = hand.winner_index

        print("🧾 Saving hand to DB:", {
            "players": players,
            "actions": actions,
            "board_cards": board_cards,
            "stacks": stacks,
            "winner_index": winner_index
        })

        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO hands (players, actions, board_cards, stacks, winner_index)
                VALUES (%s::text[], %s::jsonb, %s::text[], %s::numeric[], %s)
                RETURNING hand_id, created_at;
            """, (
                players,
                json.dumps(actions),
                board_cards,
                stacks,
                winner_index
            ))
            row = cur.fetchone()
            hand.hand_id, hand.created_at = row

        self.conn.commit()
        return hand


    def get_all_hands(self) -> List[Hand]:
        with self.conn.cursor() as cur:
            cur.execute("SELECT hand_id, players, actions, board_cards, stacks, winner_index, created_at FROM hands ORDER BY created_at DESC;")
            rows = cur.fetchall()
        return [
            Hand(
                hand_id=r[0],
                players=r[1],
                actions=r[2],
                board_cards=r[3],
                stacks=[float(s) for s in r[4]],
                winner_index=r[5],
                created_at=r[6],
            )
            for r in rows
        ]


    def get_all_hands(self) -> List[Hand]:
        with self.conn.cursor() as cur:
            cur.execute("SELECT hand_id, players, actions, board_cards, stacks, winner_index, created_at FROM hands ORDER BY created_at DESC;")
            rows = cur.fetchall()
        return [
            Hand(
                hand_id=r[0],
                players=r[1],
                actions=r[2],
                board_cards=r[3],
                stacks=[float(s) for s in r[4]],
                winner_index=r[5],
                created_at=r[6],
            )
            for r in rows
        ]
