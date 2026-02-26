from db import execute_query

def add_club(name):
    if not name or name.strip() == "":
        return "❌ Името не може да е празно."

    query = "INSERT INTO clubs (name) VALUES (?)"
    result = execute_query(query, (name.strip(),))

    if result:
        return f"✅ Клуб '{name}' е добавен."
    return "❌ Грешка или клубът вече съществува."


def get_all_clubs():
    query = "SELECT * FROM clubs"
    rows = execute_query(query, fetch=True)

    if not rows:
        return "⚠️ Няма добавени клубове."

    response = "📋 Списък с клубове:\n"
    for row in rows:
        response += f"- {row['name']}\n"

    return response


def delete_club(name):
    if not name or name.strip() == "":
        return "❌ Посочете име на клуб."

    query = "DELETE FROM clubs WHERE name = ?"
    result = execute_query(query, (name.strip(),))

    if result:
        return f"🗑️ Клуб '{name}' е изтрит (ако е съществувал)."
    return "❌ Грешка при изтриване."