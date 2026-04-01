import re
from repositories.leagues_repo import (
    create_league, get_league_by_name_season, add_team_to_league,
    remove_team_from_league, get_teams_in_league, get_club_by_name,
    delete_matches_by_league, insert_match, get_matches_by_league
)

def validate_season(season):
    # Validate format YYYY/YYYY
    if not re.match(r'^\d{4}/\d{4}$', season):
        return False
    start, end = season.split('/')
    return int(end) == int(start) + 1

def create_league_service(name, season):
    if not validate_season(season):
        return "❌ Невалиден формат на сезона. Използвай YYYY/YYYY (напр. 2025/2026)."
    
    if get_league_by_name_season(name, season):
        return f"❌ Лигата '{name}' за сезон '{season}' вече съществува."
    
    result = create_league(name, season)
    if result:
        league = get_league_by_name_season(name, season)
        return f"✅ Лигата '{name}' за сезон '{season}' е създадена с ID {league['id']}."
    else:
        return "❌ Грешка при създаване на лигата."

def add_team_to_league_service(club_name, league_name, season):
    club = get_club_by_name(club_name)
    if not club:
        return f"❌ Клубът '{club_name}' не съществува. Използвай: Покажи всички клубове"
    
    league = get_league_by_name_season(league_name, season)
    if not league:
        return f"❌ Няма лига с име '{league_name}' сезон '{season}'."
    
    teams = get_teams_in_league(league['id'])
    if any(t['id'] == club['id'] for t in teams):
        return f"❌ Клубът '{club_name}' вече е добавен в лигата."
    
    result = add_team_to_league(league['id'], club['id'])
    if result:
        return f"✅ Клубът '{club_name}' е добавен в лигата '{league_name}' {season}."
    else:
        return "❌ Грешка при добавяне на клуба."

def remove_team_from_league_service(club_name, league_name, season):
    club = get_club_by_name(club_name)
    if not club:
        return f"❌ Клубът '{club_name}' не съществува."
    
    league = get_league_by_name_season(league_name, season)
    if not league:
        return f"❌ Няма лига с име '{league_name}' сезон '{season}'."
    
    # Check if matches exist
    matches = get_matches_by_league(league['id'])
    if matches:
        return "❌ Не може да премахнеш отбор, ако има генерирана програма. Изтрий програмата първо."
    
    result = remove_team_from_league(league['id'], club['id'])
    if result:
        return f"✅ Клубът '{club_name}' е премахнат от лигата '{league_name}' {season}."
    else:
        return "❌ Грешка при премахване на клуба."

def show_teams_in_league_service(league_name, season):
    league = get_league_by_name_season(league_name, season)
    if not league:
        return f"❌ Няма лига с име '{league_name}' сезон '{season}'."
    
    teams = get_teams_in_league(league['id'])
    if not teams:
        return f"📋 Лигата '{league_name}' {season} няма отбори."
    
    response = f"📋 Отбори в лигата '{league_name}' {season}:\n"
    for team in teams:
        response += f"- {team['id']}: {team['name']}\n"
    return response.strip()

def generate_schedule_service(league_name, season):
    league = get_league_by_name_season(league_name, season)
    if not league:
        return f"❌ Няма лига с име '{league_name}' сезон '{season}'."
    
    teams = get_teams_in_league(league['id'])
    if len(teams) < 4:
        return "❌ Недостатъчно отбори за програма (минимум 4)."
    
    # Check if matches already exist
    existing_matches = get_matches_by_league(league['id'])
    if existing_matches:
        return "❌ Програмата вече е генерирана. Изтрий старата програма първо."
    
    # Delete any existing matches (though we checked)
    delete_matches_by_league(league['id'])
    
    # Generate round-robin schedule
    team_ids = [t['id'] for t in teams]
    n = len(team_ids)
    
    if n % 2 == 1:
        # Odd number, add BYE
        team_ids.append(None)  # BYE
        n += 1
    
    rounds = n - 1
    matches = []
    
    for round_num in range(1, rounds + 1):
        for i in range(n // 2):
            home = team_ids[i]
            away = team_ids[n - 1 - i]
            if home is not None and away is not None:
                matches.append((round_num, home, away))
        
        # Rotate teams
        team_ids.insert(1, team_ids.pop())
    
    # Insert matches
    for round_no, home, away in matches:
        insert_match(league['id'], round_no, home, away)
    
    total_matches = len(matches)
    first_round = [m for m in matches if m[0] == 1]
    
    response = f"✅ Програма за '{league_name}' {season} е генерирана.\n"
    response += f"Кръгове: {rounds}\n"
    response += f"Общо мачове: {total_matches}\n"
    response += "Примерен 1-ви кръг:\n"
    for _, home, away in first_round:
        home_name = next(t['name'] for t in teams if t['id'] == home)
        away_name = next(t['name'] for t in teams if t['id'] == away)
        response += f"- {home_name} vs {away_name}\n"
    
    return response.strip()
