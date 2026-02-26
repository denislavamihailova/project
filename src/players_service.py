from db import execute_query

# Добавяне на играч
def add_player(name, birthdate=None, club_name=None):
    if not name or name.strip() == "":
        return "❌ Името на играча не може да е празно."

    club_id = None
    if club_name:
        query = "SELECT id FROM clubs WHERE name = ?"
        rows = execute_query(query, (club_name.strip(),), fetch=True)
        if rows:
            club_id = rows[0]["id"]
        else:
            return f"❌ Клуб '{club_name}' не е намерен."

    query = "INSERT INTO players (name, birthdate, club_id) VALUES (?, ?, ?)"
    result = execute_query(query, (name.strip(), birthdate, club_id))
    return f"✅ Играч '{name}' е добавен." if result else "❌ Грешка при добавяне на играч."


# Премахване на играч
def delete_player(name):
    if not name or name.strip() == "":
        return "❌ Посочете име на играча."

    query = "DELETE FROM players WHERE name = ?"
    result = execute_query(query, (name.strip(),))
    return f"🗑️ Играч '{name}' е изтрит (ако съществуваше)." if result else "❌ Грешка при изтриване."


# Показване на всички играчи (по избор)
def get_all_players():
    query = """
        SELECT p.name, p.birthdate, c.name as club
        FROM players p
        LEFT JOIN clubs c ON p.club_id = c.id
    """
    rows = execute_query(query, fetch=True)
    if not rows:
        return "⚠️ Няма добавени играчи."

    response = "📋 Списък с играчи:\n"
    for r in rows:
        club = r["club"] if r["club"] else "Без клуб"
        birth = r["birthdate"] if r["birthdate"] else "Без дата на раждане"
        response += f"- {r['name']} | {birth} | {club}\n"
    return response