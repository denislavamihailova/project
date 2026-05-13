"""
Тестов скрипт за Етап 7: Класиране
Сценарии за тестване на функионалност
"""

import sys
from pathlib import Path

# Добавь src към path
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from db import execute_query, execute_script
from repositories.leagues_repo import get_league_by_name_season
from services.standings_service import calculate_standings, format_standings_compact
from utils.logger import get_logger

def setup_test_data():
    """Подготви тестови данни за проверки"""
    print("🔧 Подготовка на тестови данни...")
    
    # Очисти старите мачове
    execute_query("DELETE FROM matches WHERE league_id IN (SELECT id FROM leagues WHERE name = 'Test League')")
    execute_query("DELETE FROM league_teams WHERE league_id IN (SELECT id FROM leagues WHERE name = 'Test League')")
    execute_query("DELETE FROM leagues WHERE name = 'Test League'")
    
    # Добавь клубове
    clubs = ['Arsenal', 'Liverpool', 'Chelsea', 'Man United']
    for club in clubs:
        execute_query("INSERT OR IGNORE INTO clubs (name) VALUES (?)", (club,))
    
    # Добавь лига
    execute_query("INSERT INTO leagues (name, season) VALUES (?, ?)", ('Test League', '2025/2026'))
    league = get_league_by_name_season('Test League', '2025/2026')
    league_id = league['id']
    
    # Добавь отбори в лига
    for club in clubs:
        club_data = execute_query("SELECT id FROM clubs WHERE name = ?", (club,), fetch=True)
        if club_data:
            club_id = club_data[0]['id']
            execute_query("INSERT INTO league_teams (league_id, club_id) VALUES (?, ?)", (league_id, club_id))
    
    print(f"✅ Лига '{league_id}' създобрадена с {len(clubs)} отбора")
    return league_id

def test_scenario_1():
    """Сценарий 1: Лига с отбори, но без изиграни мачове"""
    print("\n" + "="*60)
    print("TEST 1: Лига без изиграни мачове")
    print("="*60)
    
    league_id = setup_test_data()
    
    result = calculate_standings('Test League', '2025/2026')
    
    if result['success']:
        print("✅ SUCCESS")
        table = format_standings_compact(result)
        print(table)
    else:
        print(f"❌ ERROR: {result['message']}")
    
    logger = get_logger()
    logger.log_command("test_scenario_1", "show_standings", None, "TEST 1 COMPLETED", "OK")

def test_scenario_2():
    """Сценарий 2: Един изигран мач 2:1"""
    print("\n" + "="*60)
    print("TEST 2: Един мач (2:1)")
    print("="*60)
    
    # Подготовка
    execute_query("DELETE FROM matches WHERE league_id IN (SELECT id FROM leagues WHERE name = 'Test League')")
    league = get_league_by_name_season('Test League', '2025/2026')
    league_id = league['id']
    
    # Вземи первите два отбора
    teams_data = execute_query(
        "SELECT c.id FROM clubs c JOIN league_teams lt ON c.id = lt.club_id WHERE lt.league_id = ? LIMIT 2",
        (league_id,),
        fetch=True
    )
    
    home_id = teams_data[0]['id']
    away_id = teams_data[1]['id']
    
    # Добавь мач
    execute_query(
        "INSERT INTO matches (league_id, round_no, home_club_id, away_club_id, home_goals, away_goals, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (league_id, 1, home_id, away_id, 2, 1, 'played')
    )
    
    result = calculate_standings('Test League', '2025/2026')
    
    if result['success']:
        print("✅ SUCCESS")
        standings = result['standings']
        # Проверь домакина
        home_team = next((t for t in standings if t['id'] == home_id), None)
        away_team = next((t for t in standings if t['id'] == away_id), None)
        
        print(f"Домакин: {home_team['name']} - {home_team['W']}W {home_team['D']}D {home_team['L']}L "
              f"{home_team['GF']}:{home_team['GA']} {home_team['PTS']}pts")
        print(f"Гост: {away_team['name']} - {away_team['W']}W {away_team['D']}D {away_team['L']}L "
              f"{away_team['GF']}:{away_team['GA']} {away_team['PTS']}pts")
        
        # Провери стойности
        assert home_team['W'] == 1 and home_team['PTS'] == 3, "Домакин трябва да има 1W и 3 пта"
        assert away_team['L'] == 1 and away_team['PTS'] == 0, "Гост трябва да има 1L и 0 пта"
        print("✅ Всички проверки PASS")
    else:
        print(f"❌ ERROR: {result['message']}")
    
    logger = get_logger()
    logger.log_command("test_scenario_2", "show_standings", None, "TEST 2 COMPLETED", "OK")

def test_scenario_3():
    """Сценарий 3: Несъществуваща лига"""
    print("\n" + "="*60)
    print("TEST 3: Несъществуваща лига")
    print("="*60)
    
    result = calculate_standings('Fake League', '2025/2026')
    
    if not result['success']:
        print("✅ SUCCESS - Коректно върши грешка")
        print(f"Message: {result['message']}")
    else:
        print("❌ ERROR - Трябваше да върши грешка")
    
    logger = get_logger()
    logger.log_command("test_scenario_3", "show_standings", None, "TEST 3 COMPLETED", "OK")

if __name__ == '__main__':
    print("🧪 ТЕСТВАНЕ НА ЕТАП 7: КЛАСИРАНЕ\n")
    
    try:
        test_scenario_1()
        test_scenario_2()
        test_scenario_3()
        print("\n" + "="*60)
        print("✅ ВСЕ ТЕСТОВЕ ЗАВЪРШИХА")
        print("="*60)
    except Exception as e:
        print(f"\n❌ КРИТИЧНА ГРЕШКА: {e}")
        import traceback
        traceback.print_exc()
        logger = get_logger()
        logger.log_error("test_standings", f"CRITICAL ERROR: {e}")








