from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from poker_backend.routes import hand_routes
from poker_backend.db.connection import get_connection
from poker_backend.repositories.hand_repository import HandRepository

app = FastAPI(title="Poker Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or restrict to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create table on startup
@app.on_event("startup")
def startup_event():
    conn = get_connection()
    HandRepository(conn).create_table()
    print("✅ Connected to PostgreSQL and ensured 'hands' table exists.")

# Register routes
app.include_router(hand_routes.router)

@app.get("/")
def root():
    return {"message": "Poker backend is running!"}
