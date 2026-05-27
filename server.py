import sqlite3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScanRequest(BaseModel):
    tg_id: int
    query: str

class MirrorRequest(BaseModel):
    tg_id: int
    bot_name: str

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/api/profile/{tg_id}")
async def get_profile(tg_id: int):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE tg_id = ?', (tg_id,)).fetchone()
    conn.close()
    
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
        
    return {
        "tg_id": user["tg_id"],
        "username": user["username"],
        "searches_count": user["searches_count"],
        "search_limits": user["search_limits"],
        "stars_balance": user["stars_balance"]
    }

@app.get("/api/mirrors/{tg_id}")
async def get_mirrors(tg_id: int):
    conn = get_db_connection()
    rows = conn.execute('SELECT bot_name, users_count, status FROM mirrors WHERE creator_id = ?', (tg_id,)).fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

@app.post("/api/scan")
async def execute_scan(req: ScanRequest):
    conn = get_db_connection()
    user = conn.execute('SELECT search_limits, searches_count FROM users WHERE tg_id = ?', (req.tg_id,)).fetchone()
    
    if user is None:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")
        
    if user["search_limits"] <= 0:
        conn.close()
        raise HTTPException(status_code=403, detail="No limits available")
        
    new_limits = user["search_limits"] - 1
    new_searches = user["searches_count"] + 1
    
    conn.execute('UPDATE users SET search_limits = ?, searches_count = ? WHERE tg_id = ?', 
                 (new_limits, new_searches, req.tg_id))
    conn.commit()
    conn.close()
    
    return {
        "status": "success",
        "remaining_limits": new_limits,
        "data": {
            "vk": f"ID: {hash(req.query) % 10000000}",
            "whatsapp": "Статус: Активен" if len(req.query) > 5 else "Не найден",
            "telegram": f"@{req.query}_probe" if "@" not in req.query else req.query,
            "maigret": "Найдено: 3 совпадения",
            "sherlock": "Профиль обнаружен",
            "dyxless": "Привязки найдены"
        }
    }

@app.post("/api/mirror/create")
async def create_mirror(req: MirrorRequest):
    conn = get_db_connection()
    conn.execute('INSERT INTO mirrors (creator_id, bot_name, users_count, status) VALUES (?, ?, 0, "Активно")',
                 (req.tg_id, req.bot_name))
    conn.commit()
    conn.close()
    return {"status": "created"}
