For the table where players join in
player id
display name
chips
is_active

Games/Hands

each hand(round) played at the table

gameid |UUID | Unique Id.
tableid |UUID | Table where game takes place.
dealer position |INT | seatnumber of dealer.
board cards |TEXT | shared community cards.
pot |INT | Total amount bet in this hand.
status |TEXT | “preflop”, “flop”, “turn”, “river”, “showdown”, “finished”.
winnder_id |UUID | who won the hand.
created_at |TIMESTAMP | when game/hand started.
ended_at |TIMESTAMP | when game ended.

check is when if no one has raised, it shows check. if someone else raised it becomes call

remove docker volumes using: docker compose down --volumes --remove-orphans

if changes made to poetry, then add "poetry lock"
run docker compose using : docker compose up --build

to check jsut backend logs: docker compose logs -f backend
