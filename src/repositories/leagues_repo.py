from db import execute_query

def create_league(name, season):
    query = "INSERT INTO leagues (name, season) VALUES (?, ?)"
    return execute_query(query, (name, season))

def get_league_by_name_season(name, season):
    query = "SELECT * FROM leagues WHERE name = ? AND season = ?"
    result = execute_query(query, (name, season), fetch=True)
    return result[0] if result else None

def add_team_to_league(league_id, club_id):
    query = "INSERT INTO league_teams (league_id, club_id) VALUES (?, ?)"
    return execute_query(query, (league_id, club_id))

def remove_team_from_league(league_id, club_id):
    query = "DELETE FROM league_teams WHERE league_id = ? AND club_id = ?"
    return execute_query(query, (league_id, club_id))

def get_teams_in_league(league_id):
    query = """
    SELECT c.id, c.name
    FROM league_teams lt
    JOIN clubs c ON lt.club_id = c.id
    WHERE lt.league_id = ?
    """
    return execute_query(query, (league_id,), fetch=True)

def get_club_by_name(name):
    query = "SELECT * FROM clubs WHERE name = ?"
    result = execute_query(query, (name,), fetch=True)
    return result[0] if result else None

def delete_matches_by_league(league_id):
    query = "DELETE FROM matches WHERE league_id = ?"
    return execute_query(query)

def insert_match(league_id, round_no, home_club_id, away_club_id):
    query = "INSERT INTO matches (league_id, round_no, home_club_id, away_club_id) VALUES (?, ?, ?, ?)"
    return execute_query(query, (league_id, round_no, home_club_id, away_club_id))

def get_matches_by_league(league_id):
    query = "SELECT * FROM matches WHERE league_id = ? ORDER BY round_no, id"
    return execute_query(query, (league_id,), fetch=True)
