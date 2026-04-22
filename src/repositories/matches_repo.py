from db import execute_query

def get_matches_by_league_round(league_id, round_no):
    query = """
    SELECT m.id, m.round_no, m.match_date, m.home_goals, m.away_goals, m.status,
           hc.name as home_club, ac.name as away_club
    FROM matches m
    JOIN clubs hc ON m.home_club_id = hc.id
    JOIN clubs ac ON m.away_club_id = ac.id
    WHERE m.league_id = ? AND m.round_no = ?
    ORDER BY m.id
    """
    return execute_query(query, (league_id, round_no), fetch=True)

def get_match_by_id(match_id):
    query = """
    SELECT m.*, hc.name as home_club, ac.name as away_club, l.name as league_name, l.season
    FROM matches m
    JOIN clubs hc ON m.home_club_id = hc.id
    JOIN clubs ac ON m.away_club_id = ac.id
    JOIN leagues l ON m.league_id = l.id
    WHERE m.id = ?
    """
    result = execute_query(query, (match_id,), fetch=True)
    return result[0] if result else None

def update_match_score(match_id, home_goals, away_goals):
    query = "UPDATE matches SET home_goals = ?, away_goals = ?, status = 'played' WHERE id = ?"
    return execute_query(query, (home_goals, away_goals, match_id))

def insert_goal(match_id, player_id, club_id, minute, is_own_goal=0):
    query = "INSERT INTO goals (match_id, player_id, club_id, minute, is_own_goal) VALUES (?, ?, ?, ?, ?)"
    return execute_query(query, (match_id, player_id, club_id, minute, is_own_goal))

def insert_card(match_id, player_id, club_id, minute, card_type):
    query = "INSERT INTO cards (match_id, player_id, club_id, minute, card_type) VALUES (?, ?, ?, ?, ?)"
    return execute_query(query, (match_id, player_id, club_id, minute, card_type))

def get_goals_by_match(match_id):
    query = """
    SELECT g.minute, p.full_name as player_name, c.name as club_name, g.is_own_goal
    FROM goals g
    JOIN players p ON g.player_id = p.id
    JOIN clubs c ON g.club_id = c.id
    WHERE g.match_id = ?
    ORDER BY g.minute
    """
    return execute_query(query, (match_id,), fetch=True)

def get_cards_by_match(match_id):
    query = """
    SELECT ca.minute, p.full_name as player_name, c.name as club_name, ca.card_type
    FROM cards ca
    JOIN players p ON ca.player_id = p.id
    JOIN clubs c ON ca.club_id = c.id
    WHERE ca.match_id = ?
    ORDER BY ca.minute
    """
    return execute_query(query, (match_id,), fetch=True)

def get_player_by_name_club(player_name, club_name):
    query = """
    SELECT p.id, p.club_id
    FROM players p
    JOIN clubs c ON p.club_id = c.id
    WHERE p.full_name = ? AND c.name = ?
    """
    result = execute_query(query, (player_name, club_name), fetch=True)
    return result[0] if result else None

def get_club_by_name(name):
    query = "SELECT id FROM clubs WHERE name = ?"
    result = execute_query(query, (name,), fetch=True)
    return result[0] if result else None

def find_match_by_teams(home_club, away_club, league_id=None):
    query = """
    SELECT m.id, m.status
    FROM matches m
    JOIN clubs hc ON m.home_club_id = hc.id
    JOIN clubs ac ON m.away_club_id = ac.id
    WHERE hc.name = ? AND ac.name = ?
    """
    params = [home_club, away_club]
    if league_id:
        query += " AND m.league_id = ?"
        params.append(league_id)
    result = execute_query(query, tuple(params), fetch=True)
    return result
