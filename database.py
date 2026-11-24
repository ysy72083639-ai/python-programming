import sqlite3
from datetime import datetime

DB_NAME = "uno_records.db"

def init_db():
    """데이터베이스 및 테이블 초기화"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nickname TEXT UNIQUE NOT NULL,
            wins INTEGER DEFAULT 0,
            losses INTEGER DEFAULT 0,
            min_turns INTEGER DEFAULT 999,
            updated_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_result(nickname, is_win, turns):
    """게임 결과(승/패 및 최소 턴 수) 저장 및 갱신"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    cursor.execute("SELECT wins, losses, min_turns FROM records WHERE nickname = ?", (nickname,))
    row = cursor.fetchone()

    if row:
        wins, losses, min_turns = row
        if is_win:
            wins += 1
            if turns < min_turns:
                min_turns = turns
        else:
            losses += 1
        cursor.execute("""
            UPDATE records
            SET wins = ?, losses = ?, min_turns = ?, updated_at = ?
            WHERE nickname = ?
        """, (wins, losses, min_turns, now, nickname))
    else:
        wins = 1 if is_win else 0
        losses = 0 if is_win else 1
        min_turns = turns if is_win else 999
        cursor.execute("""
            INSERT INTO records (nickname, wins, losses, min_turns, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (nickname, wins, losses, min_turns, now))

    conn.commit()
    conn.close()

def get_rankings():
    """승리 횟수 및 최소 턴 기준 TOP 5 랭킹 조회"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT nickname, wins, losses, min_turns, updated_at
        FROM records
        ORDER BY wins DESC, min_turns ASC
        LIMIT 5
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows