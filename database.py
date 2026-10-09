
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "campusfix.db"


def connect():
    conn = sqlite3.connect(str(DB_PATH), timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def now():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def init_db():
    with connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                complaint TEXT NOT NULL,
                issue TEXT NOT NULL,
                category TEXT NOT NULL,
                location TEXT NOT NULL,
                priority TEXT NOT NULL,
                assigned_team TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Open',
                ai_mode TEXT NOT NULL DEFAULT 'Offline rule-based decision engine',
                created_at TEXT NOT NULL
            )
        """)

        # Add missing fields to an existing database without deleting records.
        columns = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(tickets)").fetchall()
        }

        migrations = {
            "confidence": "REAL NOT NULL DEFAULT 0.5",
            "needs_review": "INTEGER NOT NULL DEFAULT 0",
            "workflow_step": "TEXT NOT NULL DEFAULT 'Assigned'",
            "contact_name": "TEXT NOT NULL DEFAULT ''",
            "mobile_number": "TEXT NOT NULL DEFAULT ''",
        }

        for column, definition in migrations.items():
            if column not in columns:
                conn.execute(
                    f"ALTER TABLE tickets ADD COLUMN {column} {definition}"
                )

        conn.execute("""
            CREATE TABLE IF NOT EXISTS ticket_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id INTEGER NOT NULL,
                event TEXT NOT NULL,
                details TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                FOREIGN KEY(ticket_id) REFERENCES tickets(id)
                    ON DELETE CASCADE
            )
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_tickets_status
            ON tickets(status)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_tickets_priority
            ON tickets(priority)
        """)


def add_event(conn, ticket_id, event, details=""):
    conn.execute(
        """
        INSERT INTO ticket_events
            (ticket_id, event, details, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (ticket_id, event, details, now()),
    )


def create_ticket(
    complaint,
    analysis,
    contact_name="",
    mobile_number="",
):
    created_at = now()

    with connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO tickets (
                complaint, issue, category, location, priority,
                assigned_team, status, ai_mode, created_at,
                confidence, needs_review, workflow_step,
                contact_name, mobile_number
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                complaint.strip(),
                analysis["issue"],
                analysis["category"],
                analysis["location"],
                analysis["priority"],
                analysis["assigned_team"],
                "Open",
                analysis.get(
                    "ai_mode", "Offline rule-based decision engine"
                ),
                created_at,
                float(analysis.get("confidence", 0.5)),
                int(bool(analysis.get("needs_review", False))),
                "Assigned",
                contact_name.strip(),
                mobile_number.strip(),
            ),
        )

        ticket_id = cursor.lastrowid

        add_event(conn, ticket_id, "Submitted", "Complaint received.")
        add_event(
            conn,
            ticket_id,
            "Triaged",
            f"Category: {analysis['category']}; "
            f"priority: {analysis['priority']}.",
        )
        add_event(
            conn,
            ticket_id,
            "Assigned",
            f"Assigned to {analysis['assigned_team']}.",
        )

        if analysis["priority"] == "High":
            add_event(
                conn,
                ticket_id,
                "High-priority alert",
                "This ticket requires prompt staff attention.",
            )

        if analysis.get("needs_review"):
            add_event(
                conn,
                ticket_id,
                "Review flagged",
                "Staff should verify the classification.",
            )

        return ticket_id


def get_tickets():
    # Emergency/high-priority tickets always appear first.
    with connect() as conn:
        rows = conn.execute("""
            SELECT * FROM tickets
            ORDER BY
                CASE priority
                    WHEN 'High' THEN 1
                    WHEN 'Medium' THEN 2
                    ELSE 3
                END,
                CASE status
                    WHEN 'Open' THEN 1
                    WHEN 'In Progress' THEN 2
                    ELSE 3
                END,
                id DESC
        """).fetchall()

        return [dict(row) for row in rows]


def get_ticket(ticket_id):
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM tickets WHERE id = ?",
            (int(ticket_id),),
        ).fetchone()

        return dict(row) if row else None


def find_reporter_ticket(ticket_id, mobile_number):
    """Allow a reporter to check a ticket using its ID and phone number."""
    with connect() as conn:
        row = conn.execute(
            """
            SELECT * FROM tickets
            WHERE id = ? AND mobile_number = ?
            """,
            (int(ticket_id), mobile_number.strip()),
        ).fetchone()

        return dict(row) if row else None


def get_ticket_events(ticket_id):
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT event, details, created_at
            FROM ticket_events
            WHERE ticket_id = ?
            ORDER BY id ASC
            """,
            (int(ticket_id),),
        ).fetchall()

        return [dict(row) for row in rows]


def update_status(ticket_id, status):
    allowed = {"Open", "In Progress", "Resolved"}

    if status not in allowed:
        raise ValueError(f"Unsupported ticket status: {status}")

    workflow_steps = {
        "Open": "Assigned",
        "In Progress": "In Progress",
        "Resolved": "Resolved",
    }

    with connect() as conn:
        row = conn.execute(
            "SELECT status FROM tickets WHERE id = ?",
            (int(ticket_id),),
        ).fetchone()

        if row is None:
            raise ValueError("Ticket not found.")

        old_status = row["status"]

        if old_status == status:
            return

        conn.execute(
            """
            UPDATE tickets
            SET status = ?, workflow_step = ?
            WHERE id = ?
            """,
            (status, workflow_steps[status], int(ticket_id)),
        )

        add_event(
            conn,
            int(ticket_id),
            "Status changed",
            f"Status changed from {old_status} to {status}.",
        )
