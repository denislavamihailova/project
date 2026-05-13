from db import execute_query

def get_played_matches_by_league(league_id):
    """
    Вземи всички мачове със статус 'played' за дадена лига
    Връща: list of dicts с домакин, гост, голове
    """
    query = """
    SELECT m.id, m.league_id, m.round_no, m.home_club_id, m.away_club_id,
           m.home_goals, m.away_goals, m.status,
           hc.name as home_club, ac.name as away_club
    FROM matches m
    JOIN clubs hc ON m.home_club_id = hc.id
    JOIN clubs ac ON m.away_club_id = ac.id
    WHERE m.league_id = ? AND m.status = 'played'
    ORDER BY m.round_no, m.id
    """
    return execute_query(query, (league_id,), fetch=True)

def get_all_teams_in_league(league_id):
    """
    Вземи всички отбори в лига (league_teams)
    Връща: list of dicts с id и name
    """
    query = """
    SELECT c.id, c.name
    FROM league_teams lt
    JOIN clubs c ON lt.club_id = c.id
    WHERE lt.league_id = ?
    ORDER BY c.name
    """
    return execute_query(query, (league_id,), fetch=True)

def get_head_to_head_matches(league_id, team1_id, team2_id):
    """
    Вземи директни мачове между два отбора в лига
    За "отличен" критерий (tiebreaker по директни срещи)
    """
    query = """
    SELECT m.home_club_id, m.away_club_id, m.home_goals, m.away_goals, m.status
    FROM matches m
    WHERE m.league_id = ? 
      AND m.status = 'played'
      AND (
        (m.home_club_id = ? AND m.away_club_id = ?)
        OR
        (m.home_club_id = ? AND m.away_club_id = ?)
      )
    ORDER BY m.round_no
    """
    return execute_query(query, (league_id, team1_id, team2_id, team2_id, team1_id), fetch=True)

def validate_league_teams_consistency(league_id):
    """
    Проверка: всеки мач има отбори в league_teams за дадена лига
    Връща: (is_valid: bool, error_msg: str or None)
    """
    query = """
    SELECT DISTINCT m.home_club_id, m.away_club_id
    FROM matches m
    WHERE m.league_id = ?
    """
    matches = execute_query(query, (league_id,), fetch=True) or []
    
    teams_in_league_query = """
    SELECT club_id FROM league_teams WHERE league_id = ?
    """
    teams_in_league = execute_query(teams_in_league_query, (league_id,), fetch=True) or []
    valid_team_ids = {t['club_id'] for t in teams_in_league}
    
    for match in matches:
        if match['home_club_id'] not in valid_team_ids or match['away_club_id'] not in valid_team_ids:
            return False, f"Мач #{match['home_club_id']} vs #{match['away_club_id']} има отбор, който не е в лига!"
    
    return True, None

