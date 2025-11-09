CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 🃏 Hands table (main record)
CREATE TABLE IF NOT EXISTS hands (
  hand_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  players TEXT[] NOT NULL,             -- ["AhKh", "QsQd", "9c8c"]
  actions JSONB NOT NULL,              -- full list of betting actions
  board_cards TEXT[] DEFAULT '{}',     -- ["Jh", "7c", "2h", "Tc", "Qc"]
  stacks NUMERIC[] DEFAULT '{}',       -- final stack amounts
  winner_index INT,                    -- optional: which player won
  created_at TIMESTAMPTZ DEFAULT now()
);
