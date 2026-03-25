import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from db import get_connection
import re


def transfer_player(player_name, from_club, to_club, date, fee=None):

    # Проверка на дата
    if not re.match(r"\d{4}-\d{2}-\d{2}", date):
        return "❌ Невалидна дата (YYYY-MM-DD)."

    if from_club == to_club:
        return "❌ Отборите не могат да са еднакви."

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # --- Намери играча ---
        cursor.execute(
            "SELECT id, club_id FROM players WHERE full_name = ?",
            (player_name,)
        )
        player = cursor.fetchone()

        if not player:
            return "❌ Играчът не е намерен."

        player_id = player["id"]
        current_club_id = player["club_id"]

        # --- Намери from клуб ---
        cursor.execute(
            "SELECT id FROM clubs WHERE name = ?",
            (from_club,)
        )
        from_row = cursor.fetchone()

        if not from_row:
            return "❌ From клуб не съществува."

        from_club_id = from_row["id"]

        # Проверка текущ клуб
        if current_club_id != from_club_id:
            return "❌ Играчът не е в този клуб."

        # --- Намери to клуб ---
        cursor.execute(
            "SELECT id FROM clubs WHERE name = ?",
            (to_club,)
        )
        to_row = cursor.fetchone()

        if not to_row:
            return "❌ To клуб не съществува."

        to_club_id = to_row["id"]

        # --- INSERT transfer ---
        cursor.execute(
            """
            INSERT INTO transfers
            (player_id, from_club_id, to_club_id, transfer_date, fee)
            VALUES (?, ?, ?, ?, ?)
            """,
            (player_id, from_club_id, to_club_id, date, fee)
        )

        # --- UPDATE player club ---
        cursor.execute(
            "UPDATE players SET club_id = ? WHERE id = ?",
            (to_club_id, player_id)
        )

        conn.commit()

        return (
            f"✅ Трансфер успешен: "
            f"{player_name} от {from_club} в {to_club} ({date})"
        )

    except Exception as e:
        conn.rollback()
        return f"❌ Грешка при трансфер: {e}"

    finally:
        conn.close()

def list_transfers_by_player(player_name):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            t.transfer_date,
            fc.name as from_club,
            tc.name as to_club
        FROM transfers t
        JOIN players p ON t.player_id = p.id
        LEFT JOIN clubs fc ON t.from_club_id = fc.id
        JOIN clubs tc ON t.to_club_id = tc.id
        WHERE p.full_name = ?
        ORDER BY t.transfer_date
        """,
        (player_name,)
    )

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return "⚠️ Няма трансфери."

    response = "📋 Трансфери:\n"

    for r in rows:
        response += (
            f"- {r['transfer_date']}: "
            f"{r['from_club']} → {r['to_club']}\n"
        )

    return response


def list_transfers_by_club(club_name):
    """List all transfers involving a specific club (incoming and outgoing)"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            t.transfer_date,
            p.full_name as player_name,
            fc.name as from_club,
            tc.name as to_club,
            'OUT' as direction
        FROM transfers t
        JOIN players p ON t.player_id = p.id
        LEFT JOIN clubs fc ON t.from_club_id = fc.id
        JOIN clubs tc ON t.to_club_id = tc.id
        WHERE fc.name = ? OR tc.name = ?
        ORDER BY t.transfer_date DESC
        """,
        (club_name, club_name)
    )

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return f"⚠️ Няма трансфери за {club_name}."

    response = f"📋 Трансфери на {club_name}:\n"

    for r in rows:
        response += (
            f"- {r['transfer_date']}: {r['player_name']} "
            f"({r['from_club']} → {r['to_club']})\n"
        )

    return response
