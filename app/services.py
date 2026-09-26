import json
from datetime import datetime, timezone
from .db import get_conn
from .classifier import classify
from .emailer import send_ticket_email

FLOW_NAME = "Auto Classify School IT Tickets"

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def next_number(conn) -> str:
    row = conn.execute("SELECT number FROM tickets ORDER BY id DESC LIMIT 1").fetchone()
    if not row:
        return "INC000001"
    try:
        n = int(row["number"].replace("INC", "")) + 1
    except ValueError:
        n = conn.execute("SELECT COUNT(*) + 1 AS n FROM tickets").fetchone()["n"]
    return f"INC{n:06d}"

def row_to_dict(row):
    if row is None:
        return None
    return dict(row)

def create_ticket(payload):
    ts = now()
    with get_conn() as conn:
        number = next_number(conn)
        cur = conn.execute(
            """INSERT INTO tickets(number,caller_name,caller_email,short_description,description,state,assigned_group,assigned_to,created_at,updated_at)
               VALUES(?,?,?,?,?,?,?,?,?,?)""",
            (number, payload.caller_name, str(payload.caller_email), payload.short_description,
             payload.description, payload.state, payload.assigned_group, payload.assigned_to, ts, ts)
        )
        ticket_id = cur.lastrowid
        conn.execute(
            "INSERT INTO flow_runs(ticket_id,flow_name,action,details,created_at) VALUES(?,?,?,?,?)",
            (ticket_id, FLOW_NAME, "Trigger: Record Created", "Category is empty", ts)
        )
    # Flow-style classification after creation.
    result = classify(payload.short_description, payload.description)
    with get_conn() as conn:
        conn.execute(
            "UPDATE tickets SET category=?, subcategory=?, updated_at=? WHERE id=?",
            (result.category, result.subcategory, now(), ticket_id)
        )
        conn.execute(
            "INSERT INTO flow_runs(ticket_id,flow_name,action,details,created_at) VALUES(?,?,?,?,?)",
            (ticket_id, FLOW_NAME, "Classification", json.dumps(result.model_dump()), now())
        )
    email_status = send_ticket_email(ticket_id, str(payload.caller_email), number, result.category, result.subcategory)
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO flow_runs(ticket_id,flow_name,action,details,created_at) VALUES(?,?,?,?,?)",
            (ticket_id, FLOW_NAME, "Send Email", json.dumps({"recipient": str(payload.caller_email), "status": email_status}), now())
        )
        row = conn.execute("SELECT * FROM tickets WHERE id=?", (ticket_id,)).fetchone()
    return row_to_dict(row), result, email_status

def get_ticket(ticket_id: int):
    with get_conn() as conn:
        return row_to_dict(conn.execute("SELECT * FROM tickets WHERE id=?", (ticket_id,)).fetchone())

def list_tickets():
    with get_conn() as conn:
        return [row_to_dict(r) for r in conn.execute("SELECT * FROM tickets ORDER BY id DESC").fetchall()]

def update_ticket(ticket_id: int, changes: dict):
    allowed = {k: v for k, v in changes.items() if v is not None and k in {
        "caller_name", "caller_email", "short_description", "description", "state", "assigned_group", "assigned_to"
    }}
    if "state" in allowed and allowed["state"] not in {"New", "In progress", "On hold", "Resolved", "Closed"}:
        raise ValueError("Invalid state")
    if not allowed:
        return get_ticket(ticket_id)
    allowed["updated_at"] = now()
    set_sql = ", ".join(f"{k}=?" for k in allowed)
    values = list(allowed.values()) + [ticket_id]
    with get_conn() as conn:
        cur = conn.execute(f"UPDATE tickets SET {set_sql} WHERE id=?", values)
        if cur.rowcount == 0:
            return None
        conn.execute(
            "INSERT INTO flow_runs(ticket_id,flow_name,action,details,created_at) VALUES(?,?,?,?,?)",
            (ticket_id, FLOW_NAME, "Manual Update", json.dumps(changes), now())
        )
        return row_to_dict(conn.execute("SELECT * FROM tickets WHERE id=?", (ticket_id,)).fetchone())

def dashboard():
    with get_conn() as conn:
        total = conn.execute("SELECT COUNT(*) n FROM tickets").fetchone()["n"]
        categories = [dict(r) for r in conn.execute("SELECT COALESCE(category,'Unclassified') label, COUNT(*) count FROM tickets GROUP BY category ORDER BY count DESC").fetchall()]
        subcategories = [dict(r) for r in conn.execute("SELECT COALESCE(subcategory,'Unclassified') label, COUNT(*) count FROM tickets GROUP BY subcategory ORDER BY count DESC").fetchall()]
        states = [dict(r) for r in conn.execute("SELECT state label, COUNT(*) count FROM tickets GROUP BY state ORDER BY count DESC").fetchall()]
        emails = [dict(r) for r in conn.execute("SELECT status label, COUNT(*) count FROM email_logs GROUP BY status ORDER BY count DESC").fetchall()]
    return {"total": total, "categories": categories, "subcategories": subcategories, "states": states, "emails": emails}

def history(ticket_id: int):
    with get_conn() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM flow_runs WHERE ticket_id=? ORDER BY id", (ticket_id,)).fetchall()]

def email_history():
    with get_conn() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM email_logs ORDER BY id DESC").fetchall()]
