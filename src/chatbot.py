import re
from clubs_service import add_club, get_all_clubs, delete_club
from players_service import add_player, delete_player, get_all_players

def parse_command(user_input):
    user_input = user_input.lower()

    # HELP
    if re.search(r"\b(помощ|help)\b", user_input):
        return "help", None

    # EXIT
    if re.search(r"\b(изход|exit)\b", user_input):
        return "exit", None

    # CLUB COMMANDS
    match = re.search(r"добави клуб (.+)", user_input)
    if match:
        return "add_club", match.group(1)

    if re.search(r"(покажи всички клубове|list clubs)", user_input):
        return "list_clubs", None

    match = re.search(r"изтрий клуб (.+)", user_input)
    if match:
        return "delete_club", match.group(1)

    match = re.search(r"преименувай клуб (.+) (.+)", user_input)
    if match:
        return "update_club", (match.group(1), match.group(2))

    match = re.search(r"покажи клуб (.+)", user_input)
    if match:
        return "show_club", match.group(1)

    if re.search(r"(брой клубове|колко клуба има)", user_input):
        return "count_clubs", None

    # PLAYER COMMANDS
    match = re.search(r"добави играч (.+?)(?: (\d{4}-\d{2}-\d{2}))?(?: към клуб (.+))?$", user_input)
    if match:
        name = match.group(1)
        birthdate = match.group(2)
        club_name = match.group(3)
        return "add_player", (name, birthdate, club_name)

    match = re.search(r"изтрий играч (.+)", user_input)
    if match:
        return "delete_player", match.group(1)

    if re.search(r"(покажи всички играчи|list players)", user_input):
        return "list_players", None

    return "unknown", None

def handle_intent(intent, param):
    # HELP
    if intent == "help":
        return """
📖 Налични команди:
- Добави клуб <име>
- Покажи всички клубове
- Изтрий клуб <име>
- Добави играч <име> към клуб <име на клуб>
- Изтрий играч <име>
- Покажи всички играчи
- помощ
- изход
"""

    # CLUBS
    if intent == "add_club":
        return add_club(param)
    if intent == "list_clubs":
        return get_all_clubs()
    if intent == "delete_club":
        return delete_club(param)



    # PLAYERS
    if intent == "add_player":
        name, birthdate, club_name = param
        return add_player(name, birthdate, club_name)
    if intent == "delete_player":
        return delete_player(param)
    if intent == "list_players":
        return get_all_players()

    # EXIT
    if intent == "exit":
        return "👋 Изход от системата."

    return "❓ Не разбирам командата."