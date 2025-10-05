# src/ledger/sql_ledger.py
import sqlite3, json, hashlib, time, os
DB = os.path.join(os.path.dirname(__file__), "..", "exoai_ledger.db")
DB = os.path.abspath(DB)

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS ledger (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hash TEXT,
        type TEXT,
        timestamp REAL,
        data TEXT,
        prev_hash TEXT
    )""")
    conn.commit()
    conn.close()

def _compute_hash(obj):
    s = json.dumps(obj, sort_keys=True, separators=(',',':'))
    return hashlib.sha256(s.encode()).hexdigest()

def append_entry(entry_type, data):
    init_db()
    ts = time.time()
    payload = {"type": entry_type, "timestamp": ts, "data": data}
    h = _compute_hash(payload)
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT hash FROM ledger ORDER BY id DESC LIMIT 1")
    prev = c.fetchone()
    prev = prev[0] if prev else ""
    c.execute("INSERT INTO ledger (hash,type,timestamp,data,prev_hash) VALUES (?,?,?,?,?)",
              (h, entry_type, ts, json.dumps(data), prev))
    conn.commit()
    conn.close()
    return h

def list_entries(limit=100):
    init_db()
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id,hash,type,timestamp,data,prev_hash FROM ledger ORDER BY id DESC LIMIT ?", (limit,))
    rows = c.fetchall(); conn.close()
    out=[]
    for r in rows:
        out.append({"id":r[0],"hash":r[1],"type":r[2],"timestamp":r[3],"data":json.loads(r[4]),"prev_hash":r[5]})
    return out
