import re
from players_service import add_player, get_players_by_club, update_player_number, delete_player
from clubs_service import add_club, get_all_clubs, delete_club
from services.transfers_service import transfer_player, list_transfers_by_player, list_transfers_by_club


def parse_command(user_input):
    user_input = user_input.strip()

    # -----------------------------
    # ➤ Добави играч
    # Формат: добави играч <име> в <клуб> позиция <GK|DF|MF|FW> номер <номер>
    # -----------------------------
    match = re.match(
        r"добави играч (.+?) в (.+?) позиция (GK|DF|MF|FW) номер (\d+)$",
        user_input,
        re.IGNORECASE
    )

    if match:
        name = match.group(1)
        club = match.group(2)
        position = match.group(3)
        number = int(match.group(4))

        # временно фиксирани стойности за birth_date и nationality
        birth_date = "2000-01-01"
        nationality = "Bulgaria"

        return "add_player", (name, birth_date, nationality, position, number, club)

    # Трансфер
    match = re.match(
        r"трансфер (.+?) от (.+?) в (.+?) (\d{4}-\d{2}-\d{2})",
        user_input,
        re.IGNORECASE
    )

    if match:
        return "transfer_player", (
            match.group(1),
            match.group(2),
            match.group(3),
            match.group(4),
            None
        )

    # Покажи трансфери
    match = re.match(
        r"покажи трансфери на (.+)",
        user_input,
        re.IGNORECASE
    )

    if match:
        return "show_transfers_player", match.group(1)


    # -----------------------------
    # ➤ Покажи играчи по клуб
    # Формат: покажи играчи на <клуб>
    # -----------------------------
    match = re.match(r"покажи играчи на (.+)", user_input, re.IGNORECASE)
    if match:
        return "list_players_by_club", match.group(1)

    # -----------------------------
    # ➤ Смени номер
    # Формат: смени номер на <име> на <номер>
    # -----------------------------
    match = re.match(r"смени номер на (.+) на (\d+)", user_input, re.IGNORECASE)
    if match:
        return "update_number", (match.group(1), int(match.group(2)))

    # -----------------------------
    # ➤ Изтрий играч
    # Формат: изтрий играч <име>
    # -----------------------------
    match = re.match(r"изтрий играч (.+)", user_input, re.IGNORECASE)
    if match:
        return "delete_player", match.group(1)

    # -----------------------------
    # ➤ Добави клуб
    # Формат: добави клуб <име>
    # -----------------------------
    match = re.match(r"добави клуб (.+)", user_input, re.IGNORECASE)
    if match:
        return "add_club", match.group(1)

    # -----------------------------
    # ➤ Покажи всички клубове
    # -----------------------------
    if user_input.lower() in ["покажи всички клубове", "list clubs"]:
        return "list_clubs", None

    # -----------------------------
    # ➤ Изтрий клуб
    # Формат: изтрий клуб <име>
    # -----------------------------
    match = re.match(r"изтрий клуб (.+)", user_input, re.IGNORECASE)
    if match:
        return "delete_club", match.group(1)

    # -----------------------------
    # ➤ Помощ
    # -----------------------------
    if user_input.lower() in ["помощ", "help"]:
        return "help", None

    # -----------------------------
    # ➤ Изход
    # -----------------------------
    if user_input.lower() in ["изход", "exit"]:
        return "exit", None

    # -----------------------------
    # Неразпозната команда
    # -----------------------------
    return None, None


def handle_intent(intent, param):
    if intent == "add_player":
        return add_player(*param)

    if intent == "list_players_by_club":
        return get_players_by_club(param)

    if intent == "update_number":
        name, num = param
        return update_player_number(name, num)

    if intent == "delete_player":
        return delete_player(param)

    if intent == "add_club":
        return add_club(param)

    if intent == "list_clubs":
        return get_all_clubs()

    if intent == "delete_club":
        return delete_club(param)

    if intent == "help":
        return (
            "📋 Достъпни команди:\n"
            "--- Клубове ---\n"
            "- добави клуб <име>\n"
            "- покажи всички клубове\n"
            "- изтрий клуб <име>\n"
            "--- Играчи ---\n"
            "- добави играч <име> в <клуб> позиция <GK|DF|MF|FW> номер <номер>\n"
            "- покажи играчи на <клуб>\n"
            "- смени номер на <име> на <номер>\n"
            "- изтрий играч <име>\n"
            "--- Трансфери ---\n"
            "- трансфер <име играч> от <клуб> в <клуб> <дата YYYY-MM-DD>\n"
            "- покажи трансфери на <име играч или клуб>\n"
            "--- Система ---\n"
            "- помощ / help\n"
            "- изход / exit"
        )

    if intent == "transfer_player":
        return transfer_player(*param)

    if intent == "show_transfers_player":
        # Auto-detect if it's a player or club by checking the database
        from db import execute_query
        name = param
        
        # Check if it's a player
        player = execute_query("SELECT id FROM players WHERE full_name = ?", (name,), fetch=True)
        if player:
            return list_transfers_by_player(name)
        
        # Check if it's a club
        club = execute_query("SELECT id FROM clubs WHERE name = ?", (name,), fetch=True)
        if club:
            return list_transfers_by_club(name)
        
        # Not found
        return f"❌ Играч или клуб '{name}' не е намерен."


    if intent == "exit":
        return "⚡ Изход от чатбота. До скоро!"

    # default
    return "❓ Не разбирам командата."