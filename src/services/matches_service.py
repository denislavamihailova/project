from repositories.matches_repo import (
    get_matches_by_league_round, get_match_by_id, update_match_score,
    insert_goal, insert_card, get_goals_by_match, get_cards_by_match,
    get_player_by_name_club, get_club_by_name, find_match_by_teams
)
from repositories.leagues_repo import get_league_by_name_season

# Global variable for current match (in a real app, this would be in session/user context)
current_match_id = None

def set_current_match(match_id):
    global current_match_id
    match = get_match_by_id(match_id)
    if match:
        current_match_id = match_id
        return f"✅ Текущият мач е зададен на #{match_id}: {match['home_club']} vs {match['away_club']}"
    else:
        return f"❌ Мач с ID {match_id} не е намерен."

def get_current_match():
    global current_match_id
    return current_match_id

def show_round_schedule(league_name, season, round_no):
    league = get_league_by_name_season(league_name, season)
    if not league:
        return f"❌ Лигата '{league_name}' {season} не съществува."
    
    matches = get_matches_by_league_round(league['id'], round_no)
    if not matches:
        return f"❌ Няма мачове за кръг {round_no} в лигата '{league_name}' {season}."
    
    response = f"📋 Кръг {round_no} - {league_name} {season}:\n"
    for match in matches:
        score = f" {match['home_goals']}:{match['away_goals']}" if match['home_goals'] is not None else ""
        status = " (played)" if match['status'] == 'played' else ""
        response += f"- #{match['id']}: {match['home_club']} - {match['away_club']}{score}{status}\n"
    return response.strip()

def record_match_score(home_club, away_club, home_goals, away_goals):
    # Find the match
    matches = find_match_by_teams(home_club, away_club)
    if not matches:
        return f"❌ Няма мач между '{home_club}' и '{away_club}'."
    if len(matches) > 1:
        return f"❌ Има няколко мача между '{home_club}' и '{away_club}'. Посочи лига/кръг."
    
    match = matches[0]
    if match['status'] == 'played':
        return f"❌ Резултатът за мач #{match['id']} вече е записан."
    
    # Validate scores
    try:
        home_goals = int(home_goals)
        away_goals = int(away_goals)
        if home_goals < 0 or away_goals < 0:
            raise ValueError
    except ValueError:
        return "❌ Невалиден резултат. Използвай цели числа >= 0."
    
    # Update score
    update_match_score(match['id'], home_goals, away_goals)
    return f"✅ Записано: {home_club}–{away_club} {home_goals}:{away_goals} (мач #{match['id']})"

def add_goal(player_name, club_name, minute):
    match_id = get_current_match()
    if not match_id:
        return "❌ Няма избран текущ мач. Използвай 'Избери мач <id>'."
    
    match = get_match_by_id(match_id)
    if not match:
        return "❌ Текущият мач не е намерен."
    
    # Validate minute
    try:
        minute = int(minute)
        if minute < 1 or minute > 120:
            raise ValueError
    except ValueError:
        return "❌ Невалидна минута. Трябва да е цяло число между 1 и 120."
    
    # Get player
    player = get_player_by_name_club(player_name, club_name)
    if not player:
        return f"❌ Играч '{player_name}' не е намерен в клуб '{club_name}'."
    
    # Check if club is in the match
    if player['club_id'] not in [match['home_club_id'], match['away_club_id']]:
        return f"❌ Клубът '{club_name}' не участва в този мач."
    
    # Insert goal
    insert_goal(match_id, player['id'], player['club_id'], minute)
    return f"✅ Гол: {player_name} ({club_name}) в {minute}'"

def add_card(player_name, club_name, card_type, minute):
    match_id = get_current_match()
    if not match_id:
        return "❌ Няма избран текущ мач. Използвай 'Избери мач <id>'."
    
    match = get_match_by_id(match_id)
    if not match:
        return "❌ Текущият мач не е намерен."
    
    # Validate card_type
    if card_type not in ['Y', 'R']:
        return "❌ Невалиден тип картон. Използвай 'Y' или 'R'."
    
    # Validate minute
    try:
        minute = int(minute)
        if minute < 1 or minute > 120:
            raise ValueError
    except ValueError:
        return "❌ Невалидна минута. Трябва да е цяло число между 1 и 120."
    
    # Get player
    player = get_player_by_name_club(player_name, club_name)
    if not player:
        return f"❌ Играч '{player_name}' не е намерен в клуб '{club_name}'."
    
    # Check if club is in the match
    if player['club_id'] not in [match['home_club_id'], match['away_club_id']]:
        return f"❌ Клубът '{club_name}' не участва в този мач."
    
    # Insert card
    insert_card(match_id, player['id'], player['club_id'], minute, card_type)
    card_desc = "жълт" if card_type == 'Y' else "червен"
    return f"✅ {card_desc.capitalize()} картон: {player_name} ({club_name}) в {minute}'"

def show_match_events(match_id=None):
    if match_id is None:
        match_id = get_current_match()
    if not match_id:
        return "❌ Няма избран мач. Използвай 'Покажи събития <id>' или избери мач."
    
    match = get_match_by_id(match_id)
    if not match:
        return f"❌ Мач с ID {match_id} не е намерен."
    
    goals = get_goals_by_match(match_id)
    cards = get_cards_by_match(match_id)
    
    response = f"📋 Събития за мач #{match_id}: {match['home_club']} vs {match['away_club']}\n"
    
    if not goals and not cards:
        response += "Няма събития."
        return response
    
    events = []
    for goal in goals:
        own = " (автогол)" if goal['is_own_goal'] else ""
        events.append((goal['minute'], f"Гол: {goal['player_name']} ({goal['club_name']})'{own}"))
    
    for card in cards:
        card_desc = "Жълт" if card['card_type'] == 'Y' else "Червен"
        events.append((card['minute'], f"{card_desc} картон: {card['player_name']} ({card['club_name']})'"))
    
    events.sort(key=lambda x: x[0])
    
    for minute, desc in events:
        response += f"{minute}': {desc}\n"
    
    return response.strip()
