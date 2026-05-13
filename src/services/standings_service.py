"""
Модул за изчисляване на класиране в лига
Алгоритъм:
1. Вземи всички отбори в лига
2. Инициализирай статистика (MP=0, W=D=L=0, GF=GA=0, PTS=0)
3. За всеки изигран мач: актуализирай статистика
4. Изчисли голова разлика (GD)
5. Сортирай по ясни правила (точки, GD, GF, име)
6. Форматирай за печат
"""

from repositories.standings_repo import (
    get_played_matches_by_league,
    get_all_teams_in_league,
    get_head_to_head_matches,
    validate_league_teams_consistency
)
from repositories.leagues_repo import get_league_by_name_season
from utils.logger import get_logger

def calculate_standings(league_name, season):
    """
    Главна функция за изчисляване на класиране
    
    Параметри:
        league_name (str): Име на лига
        season (str): Сезон (формат: YYYY/YYYY)
    
    Връща:
        dict: {
            'success': bool,
            'message': str,
            'standings': list of dicts (or None if error)
        }
    """
    
    # Вземи лига
    league = get_league_by_name_season(league_name, season)
    if not league:
        msg = f"❌ Лигата '{league_name}' сезон '{season}' не съществува."
        logger = get_logger()
        logger.log_error(f"show_standings {league_name} {season}", msg)
        return {'success': False, 'message': msg, 'standings': None}
    
    league_id = league['id']
    
    # Вземи всички отбори в лига
    teams = get_all_teams_in_league(league_id)
    if not teams:
        msg = f"❌ Лигата '{league_name}' {season} няма добавени отбори."
        logger = get_logger()
        logger.log_error(f"show_standings {league_name} {season}", msg)
        return {'success': False, 'message': msg, 'standings': None}
    
    # Валидация на консистентност
    is_valid, error_msg = validate_league_teams_consistency(league_id)
    if not is_valid:
        logger = get_logger()
        logger.log_error(f"standings consistency", error_msg)
    
    # Инициализирай статистика за всеки отбор
    standings = {}
    for team in teams:
        standings[team['id']] = {
            'id': team['id'],
            'name': team['name'],
            'MP': 0,      # Мачове
            'W': 0,       # Победи
            'D': 0,       # Равни
            'L': 0,       # Загуби
            'GF': 0,      # Вкарани голове
            'GA': 0,      # Допуснати голове
            'GD': 0,      # Голова разлика
            'PTS': 0      # Точки
        }
    
    # Вземи всички изиграни мачове
    played_matches = get_played_matches_by_league(league_id)
    
    # Обработи всеки мач
    for match in played_matches:
        home_id = match['home_club_id']
        away_id = match['away_club_id']
        home_goals = match['home_goals']
        away_goals = match['away_goals']
        
        # Пропусни мачове без резултат (NULL)
        if home_goals is None or away_goals is None:
            continue
        
        # Актуализирай MP (изиграни мачове)
        standings[home_id]['MP'] += 1
        standings[away_id]['MP'] += 1
        
        # Актуализирай вкарани и допуснати голове
        standings[home_id]['GF'] += home_goals
        standings[home_id]['GA'] += away_goals
        
        standings[away_id]['GF'] += away_goals
        standings[away_id]['GA'] += home_goals
        
        # Актуализирай W/D/L и PTS
        if home_goals > away_goals:
            # Домакин печели
            standings[home_id]['W'] += 1
            standings[home_id]['PTS'] += 3
            standings[away_id]['L'] += 1
        elif home_goals < away_goals:
            # Гост печели
            standings[away_id]['W'] += 1
            standings[away_id]['PTS'] += 3
            standings[home_id]['L'] += 1
        else:
            # Равен
            standings[home_id]['D'] += 1
            standings[home_id]['PTS'] += 1
            standings[away_id]['D'] += 1
            standings[away_id]['PTS'] += 1
    
    # Изчисли голова разлика за всеки отбор
    for team_id in standings:
        standings[team_id]['GD'] = standings[team_id]['GF'] - standings[team_id]['GA']
    
    # Сортирай отборите
    sorted_standings = sort_standings(list(standings.values()), league_id)
    
    logger = get_logger()
    logger.log_command(f"show_standings {league_name} {season}", "show_standings", 
                      f"{league_name} {season}", 
                      f"Standings calculated for {len(sorted_standings)} teams", "OK")
    
    return {
        'success': True,
        'message': None,
        'standings': sorted_standings,
        'league_name': league_name,
        'season': season
    }

def sort_standings(standings_list, league_id=None):
    """
    Сортира отборите по правила за класиране
    
    Правила (задължителни):
    1. Точки (низходящо)
    2. Голова разлика (низходящо)
    3. Вкарани голове (низходящо)
    4. Име на отбор (възходящо, за стабилност)
    
    За "Отличен" (директни срещи):
    Ако dois отбора имат еднакви точки И еднаква GD И еднакви GF,
    сортира по директни мачове между тях.
    """
    
    # Групирай отборите по точки/GD/GF (за директни срещи)
    groups = {}
    for team in standings_list:
        key = (team['PTS'], team['GD'], team['GF'])
        if key not in groups:
            groups[key] = []
        groups[key].append(team)
    
    # Сортирай всяка група
    result = []
    for key in sorted(groups.keys(), key=lambda x: (-x[0], -x[1], -x[2])):
        group = groups[key]
        
        if len(group) == 1:
            result.append(group[0])
        else:
            # За два или повече отбора с еднакви критерии -> директни срещи (отличен)
            if league_id:
                group_sorted = sort_by_head_to_head(group, league_id)
            else:
                # Ако няма league_id, просто сортирай по име
                group_sorted = sorted(group, key=lambda x: x['name'])
            result.extend(group_sorted)
    
    return result

def sort_by_head_to_head(teams, league_id):
    """
    Директни срещи между равни отбори (за "отличен" критерий)
    Ако все още има равенство, сортира по име.
    """
    
    if len(teams) <= 1:
        return teams
    
    # Изчисли статистика от директни мачове за всеки отбор
    h2h_stats = {}
    for team in teams:
        h2h_stats[team['id']] = {
            'team': team,
            'h2h_pts': 0,
            'h2h_gd': 0,
            'h2h_gf': 0
        }
    
    # Събери всички директни мачове между тях
    for i, team1 in enumerate(teams):
        for team2 in teams[i + 1:]:
            matches = get_head_to_head_matches(league_id, team1['id'], team2['id'])
            
            for match in matches:
                home_id = match['home_club_id']
                away_id = match['away_club_id']
                home_goals = match['home_goals']
                away_goals = match['away_goals']
                
                if home_goals is None or away_goals is None:
                    continue
                
                # Актуализирай статистика
                h2h_stats[home_id]['h2h_gf'] += home_goals
                h2h_stats[home_id]['h2h_gd'] += (home_goals - away_goals)
                h2h_stats[away_id]['h2h_gf'] += away_goals
                h2h_stats[away_id]['h2h_gd'] += (away_goals - home_goals)
                
                # Точки от H2H
                if home_goals > away_goals:
                    h2h_stats[home_id]['h2h_pts'] += 3
                elif home_goals < away_goals:
                    h2h_stats[away_id]['h2h_pts'] += 3
                else:
                    h2h_stats[home_id]['h2h_pts'] += 1
                    h2h_stats[away_id]['h2h_pts'] += 1
    
    # Сортирай по H2H критерии, после по име
    result = sorted(
        teams,
        key=lambda t: (
            -h2h_stats[t['id']]['h2h_pts'],
            -h2h_stats[t['id']]['h2h_gd'],
            -h2h_stats[t['id']]['h2h_gf'],
            t['name']
        )
    )
    
    return result

def format_standings_table(standings_data):
    """
    Форматира класирането за печат (красив вид)
    
    Връща: (Header: str, Rows: list of str)
    """
    if not standings_data or not standings_data['standings']:
        return None
    
    league_name = standings_data['league_name']
    season = standings_data['season']
    standings = standings_data['standings']
    
    header = f"📊 КЛАСИРАНЕ - {league_name} {season}\n"
    header += "=" * 80 + "\n"
    header += " №  │ Отбор               │ МИ │ П │ Р │ З │ ВГ:ДГ │ ГД  │ ПТ\n"
    header += "-" * 80
    
    rows = []
    for pos, team in enumerate(standings, 1):
        mp = team['MP']
        w = team['W']
        d = team['D']
        l = team['L']
        gf = team['GF']
        ga = team['GA']
        gd = team['GD']
        pts = team['PTS']
        
        gd_str = f"+{gd}" if gd >= 0 else str(gd)
        
        row = f"{pos:2d}. │ {team['name']:<18} │ {mp:2d} │ {w} │ {d} │ {l} │ {gf:2d}:{ga:<2d} │ {gd_str:>3} │ {pts:2d}"
        rows.append(row)
    
    return header, rows

def format_standings_compact(standings_data):
    """
    Компактен формат (еден ред на отбор)
    Формат: "1. Лудогорец 10 8 1 1 22:8 +14 25"
    """
    if not standings_data or not standings_data['standings']:
        return None
    
    league_name = standings_data['league_name']
    season = standings_data['season']
    standings = standings_data['standings']
    
    lines = [f"📊 Класиране - {league_name} {season}:\n"]
    
    for pos, team in enumerate(standings, 1):
        gd_str = f"+{team['GD']}" if team['GD'] >= 0 else str(team['GD'])
        line = (f"{pos}. {team['name']:<20} {team['MP']}  {team['W']}  {team['D']}  {team['L']}  "
                f"{team['GF']}:{team['GA']}  {gd_str:>3}  {team['PTS']}")
        lines.append(line)
    
    return "\n".join(lines)




