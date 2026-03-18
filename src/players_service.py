from db import execute_query
import re

VALID_POSITIONS = {"GK", "DF", "MF", "FW"}

def add_player(full_name, birth_date, nationality, position, number, club_name):
    # --- Валидации ---
    if position not in VALID_POSITIONS:
        return "❌ Невалидна позиция (GK, DF, MF, FW)."

    if not (1 <= number <= 99):
        return "❌ Номерът трябва да е между 1 и 99."

    if not re.match(r"\d{4}-\d{2}-\d{2}", birth_date):
        return "❌ Датата трябва да е YYYY-MM-DD."

    # --- Намираме клуба ---
    club = execute_query("SELECT id FROM clubs WHERE name = ?", (club_name,), fetch=True)
    if not club:
        return f"❌ Клуб '{club_name}' не е намерен."

    club_id = club[0]["id"]

    # --- Insert ---
    query = """
    INSERT INTO players (full_name, birth_date, nationality, position, number, club_id)
    VALUES (?, ?, ?, ?, ?, ?)
    """

    result = execute_query(query, (full_name, birth_date, nationality, position, number, club_id))

    return "✅ Играчът е добавен." if result else "❌ Грешка."



def get_players_by_club(club_name=None):
    if club_name:
        query = """
        SELECT p.full_name, p.position, p.number, c.name as club
        FROM players p
        JOIN clubs c ON p.club_id = c.id
        WHERE c.name = ?
        """
        rows = execute_query(query, (club_name,), fetch=True)
    else:
        query = """
        SELECT p.full_name, p.position, p.number, c.name as club
        FROM players p
        LEFT JOIN clubs c ON p.club_id = c.id
        """
        rows = execute_query(query, fetch=True)

    if not rows:
        return "⚠️ Няма играчи."

    response = "📋 Играчи:\n"
    for r in rows:
        response += f"- {r['full_name']} | {r['position']} | №{r['number']} | {r['club']}\n"

    return response



def update_player_number(name, new_number):
    if not (1 <= new_number <= 99):
        return "❌ Невалиден номер."

    query = "UPDATE players SET number = ? WHERE full_name = ?"
    result = execute_query(query, (new_number, name))

    return "✅ Номерът е обновен." if result else "❌ Грешка."


def delete_player(name):
    query = "DELETE FROM players WHERE full_name = ?"
    result = execute_query(query, (name,))
    return "✅ Играчът е изтрит." if result else "❌ Грешка."


# Показване на всички играчи (по избор)
def get_all_players():
    query = """
        SELECT p.name, p.number, c.name as club
        FROM players p
        LEFT JOIN clubs c ON p.club_id = c.id
    """
    rows = execute_query(query, fetch=True)

    if not rows:
        return "⚠️ Няма играчи."

    response = "📋 Играчи:\n"
    for r in rows:
        club = r["club"] if r["club"] else "Без клуб"
        number = r["number"] if r["number"] else "-"
        response += f"- {r['name']} | №{number} | {club}\n"

    return response