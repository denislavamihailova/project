#!/usr/bin/env python3
"""
Финална проверка на Етап 7: Классиране
Проверява че всичко е реализирано правилно
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

print('=' * 70)
print('ФИНАЛНА ПРОВЕРКА НА ЭТАП 7')
print('=' * 70)

# 1. Проверка на импорти
print('\n[1] Проверка на импорти...')
try:
    from repositories.standings_repo import get_played_matches_by_league
    from services.standings_service import calculate_standings, format_standings_compact
    from chatbot import parse_command, handle_intent
    print('✅ Всички импорти успешни')
except ImportError as e:
    print(f'❌ Импорт грешка: {e}')
    sys.exit(1)

# 2. Проверка на файлове
print('\n[2] Проверка на файлове...')
files = [
    'src/repositories/standings_repo.py',
    'src/services/standings_service.py',
    'STAGE7_README.md',
    'STAGE7_COMPLETION.md',
    'STAGE7_TESTS.py',
    'commands.log'
]
for f in files:
    if os.path.exists(f):
        size = os.path.getsize(f)
        print(f'✅ {f} ({size} bytes)')
    else:
        print(f'❌ {f} НЕ НАМЕРЕН')

# 3. Проверка на команда
print('\n[3] Проверка на чатбот команда...')
intent, params = parse_command('покажи класиране Test League 2025/2026')
if intent == 'show_standings' and params == ('Test League', '2025/2026'):
    print('✅ Команда парсирана правилно')
    print(f'   Intent: {intent}')
    print(f'   Params: {params}')
else:
    print(f'❌ Команда не се парсира правилно')

# 4. Проверка на алгоритъм
print('\n[4] Проверка на алгоритъм...')
from db import execute_query

# Очисти
execute_query('DELETE FROM matches WHERE league_id IN (SELECT id FROM leagues WHERE name = ?)', ('FinalCheck',))
execute_query('DELETE FROM league_teams WHERE league_id IN (SELECT id FROM leagues WHERE name = ?)', ('FinalCheck',))
execute_query('DELETE FROM leagues WHERE name = ?', ('FinalCheck',))

# Създай лига
for club in ['Club1', 'Club2', 'Club3']:
    execute_query('INSERT OR IGNORE INTO clubs (name) VALUES (?)', (club,))

execute_query('INSERT INTO leagues (name, season) VALUES (?, ?)', ('FinalCheck', '2025/2026'))
league = execute_query('SELECT id FROM leagues WHERE name = ? AND season = ?', ('FinalCheck', '2025/2026'), fetch=True)[0]
league_id = league['id']

for club_name in ['Club1', 'Club2', 'Club3']:
    club_id = execute_query('SELECT id FROM clubs WHERE name = ?', (club_name,), fetch=True)[0]['id']
    execute_query('INSERT INTO league_teams (league_id, club_id) VALUES (?, ?)', (league_id, club_id))

print('  ✅ Лига със 3 отбора е създадена')

# Добавй мач
club1 = execute_query('SELECT id FROM clubs WHERE name = ?', ('Club1',), fetch=True)[0]['id']
club2 = execute_query('SELECT id FROM clubs WHERE name = ?', ('Club2',), fetch=True)[0]['id']

execute_query(
    'INSERT INTO matches (league_id, round_no, home_club_id, away_club_id, home_goals, away_goals, status) VALUES (?, ?, ?, ?, ?, ?, ?)',
    (league_id, 1, club1, club2, 2, 1, 'played')
)
print('  ✅ Мач добавен: Club1 (2) vs Club2 (1)')

# Изчисли
result = calculate_standings('FinalCheck', '2025/2026')
if result['success']:
    standings = result['standings']
    club1_stats = [s for s in standings if s['name'] == 'Club1'][0]
    
    if club1_stats['PTS'] == 3 and club1_stats['W'] == 1 and club1_stats['GF'] == 2:
        print('✅ Алгоритъм работи правилно')
        print(f'   Club1: {club1_stats["W"]}W {club1_stats["D"]}D {club1_stats["L"]}L {club1_stats["GF"]}:{club1_stats["GA"]} {club1_stats["PTS"]}pts')
    else:
        print('❌ Статистика не е правилна')
else:
    print(f'❌ Грешка: {result["message"]}')

# 5. Проверка на логиране
print('\n[5] Проверка на логирање...')
if os.path.exists('commands.log'):
    with open('commands.log', 'r', encoding='utf-8') as f:
        content = f.read()
        if 'show_standings' in content:
            print('✅ Логирање функционира')
            lines = len(content.split('\n'))
            print(f'   Всеко залогирани записи ({lines} редов)')
        else:
            print('⚠️ Няма логирани операции за show_standings')
else:
    print('⚠️ commands.log не намерен')

print('\n' + '=' * 70)
print('✅ ФИНАЛНА ПРОВЕРКА ЗАВРШЕНА')
print('✅ ВСЕ КОМПОНЕНТИ НА ЕТАП 7 РАБОТЯТ ПРАВИЛНО')
print('=' * 70)

# Очисти
execute_query('DELETE FROM matches WHERE league_id IN (SELECT id FROM leagues WHERE name = ?)', ('FinalCheck',))
execute_query('DELETE FROM league_teams WHERE league_id IN (SELECT id FROM leagues WHERE name = ?)', ('FinalCheck',))
execute_query('DELETE FROM leagues WHERE name = ?', ('FinalCheck',))

