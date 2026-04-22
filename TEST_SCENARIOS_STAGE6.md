# Test Scenarios - Stage 6: Matches Module

## Setup Prerequisites

Before running match tests, ensure the following data exists:

```sql
-- Clubs
INSERT INTO clubs (name) VALUES ('Левски'), ('ЦСКА'), ('Лудогорец'), ('Славия');

-- Players (with club_id)
INSERT INTO players (full_name, club_id, position) VALUES
('Иван Петров', 1, 'FW'),  -- Левски
('Петър Стоянов', 2, 'MF'), -- ЦСКА
('Георги Димитров', 3, 'DF'), -- Лудогорец
('Стоян Ангелов', 4, 'GK'); -- Славия

-- League
INSERT INTO leagues (name, season) VALUES ('Първа лига', '2025/2026');

-- League teams
INSERT INTO league_teams (league_id, club_id) VALUES
(1, 1), (1, 2), (1, 3), (1, 4);

-- Matches (generated schedule)
INSERT INTO matches (league_id, round_no, home_club_id, away_club_id) VALUES
(1, 1, 1, 2),  -- Левски vs ЦСКА
(1, 1, 3, 4);  -- Лудогорец vs Славия
```

## Test Scenarios

### 1. Show Round Schedule

#### ✅ Valid Round Display
```
Command: покажи кръг 1 Първа лига 2025/2026
Expected: 📋 Кръг 1 - Първа лига 2025/2026:
- #1: Левски - ЦСКА
- #2: Лудогорец - Славия
```

#### ❌ Invalid League
```
Command: покажи кръг 1 Несъществуваща 2025/2026
Expected: ❌ Лигата 'Несъществуваща' 2025/2026 не съществува.
```

#### ❌ No Matches in Round
```
Command: покажи кръг 10 Първа лига 2025/2026
Expected: ❌ Няма мачове за кръг 10 в лигата 'Първа лига' 2025/2026.
```

### 2. Record Match Score

#### ✅ Valid Score Recording
```
Command: резултат Левски-ЦСКА 3:0 запиши
Expected: ✅ Записано: Левски–ЦСКА 3:0 (мач #1)
```

#### ❌ Match Already Played
```
Command: резултат Левски-ЦСКА 2:1 запиши  (repeat)
Expected: ❌ Резултатът за мач #1 вече е записан.
```

#### ❌ Invalid Score Format
```
Command: резултат Левски-ЦСКА 3:-1 запиши
Expected: ❌ Невалиден резултат. Използвай цели числа >= 0.
```

#### ❌ No Such Match
```
Command: резултат Левски-Ботев 1:0 запиши
Expected: ❌ Няма мач между 'Левски' и 'Ботев'.
```

#### ❌ Multiple Matches (if applicable)
```
Command: резултат Левски-ЦСКА 1:0 запиши  (if multiple leagues have same teams)
Expected: ❌ Има няколко мача между 'Левски' и 'ЦСКА'. Посочи лига/кръг.
```

### 3. Select Current Match

#### ✅ Valid Match Selection
```
Command: избери мач 1
Expected: ✅ Текущият мач е зададен на #1: Левски vs ЦСКА
```

#### ❌ Invalid Match ID
```
Command: избери мач 999
Expected: ❌ Мач с ID 999 не е намерен.
```

### 4. Add Goal

#### ✅ Valid Goal Addition
```
Command: гол Иван Петров Левски 23 минута
Expected: ✅ Гол: Иван Петров (Левски) в 23'
```

#### ❌ No Current Match
```
Command: гол Иван Петров Левски 23 минута  (before selecting match)
Expected: ❌ Няма избран текущ мач. Използвай 'Избери мач <id>'.
```

#### ❌ Invalid Minute
```
Command: гол Иван Петров Левски 150 минута
Expected: ❌ Невалидна минута. Трябва да е цяло число между 1 и 120.
```

#### ❌ Player Not in Club
```
Command: гол Иван Петров ЦСКА 23 минута
Expected: ❌ Играч 'Иван Петров' не е намерен в клуб 'ЦСКА'.
```

#### ❌ Club Not in Match
```
Command: гол Стоян Ангелов Славия 23 минута  (if current match is Левски vs ЦСКА)
Expected: ❌ Клубът 'Славия' не участва в този мач.
```

### 5. Add Card

#### ✅ Valid Yellow Card
```
Command: картон Иван Петров Левски Y 55
Expected: ✅ Жълт картон: Иван Петров (Левски) в 55'
```

#### ✅ Valid Red Card
```
Command: картон Петър Стоянов ЦСКА R 67
Expected: ✅ Червен картон: Петър Стоянов (ЦСКА) в 67'
```

#### ❌ Invalid Card Type
```
Command: картон Иван Петров Левски X 55
Expected: ❌ Невалиден тип картон. Използвай 'Y' или 'R'.
```

#### ❌ Same validations as goals (minute, player, club)

### 6. Show Match Events

#### ✅ Show Current Match Events
```
Command: покажи събития
Expected: 📋 Събития за мач #1: Левски vs ЦСКА
23': Гол: Иван Петров (Левски)
55': Жълт картон: Иван Петров (Левски)
67': Гол: Петър Стоянов (ЦСКА)
```

#### ✅ Show Specific Match Events
```
Command: покажи събития 1
Expected: Same as above
```

#### ❌ No Current Match
```
Command: покажи събития  (before selecting match)
Expected: ❌ Няма избран мач. Използвай 'Покажи събития <id>' или избери мач.
```

#### ❌ Invalid Match ID
```
Command: покажи събития 999
Expected: ❌ Мач с ID 999 не е намерен.
```

#### ✅ No Events
```
Command: покажи събития 2  (match with no goals/cards)
Expected: 📋 Събития за мач #2: Лудогорец vs Славия
Няма събития.
```

## Full Test Flow

1. **Setup:** Create clubs, players, league, teams, matches
2. **Show round:** Verify matches display correctly
3. **Select match:** Choose match #1
4. **Add goals:** Add goals for both teams
5. **Add cards:** Add yellow and red cards
6. **Show events:** Verify chronological display
7. **Record score:** Set final score
8. **Show round again:** Verify updated status/scores
9. **Error tests:** Try invalid operations

## Logging Verification

After each command, check `commands.log` contains:
- Timestamp
- Raw command
- Intent (e.g., "show_round", "record_score")
- Status: "OK" or "ERROR"
- Response message

Example log entries:
```
2026-04-22 15:00:00 | покажи кръг 1 Първа лига 2025/2026 | show_round | OK | 📋 Кръг 1 - Първа лига 2025/2026:...
2026-04-22 15:01:00 | резултат Левски-ЦСКА 3:0 запиши | record_score | OK | ✅ Записано: Левски–ЦСКА 3:0 (мач #1)
2026-04-22 15:02:00 | гол Иван Петров Левски 23 минута | add_goal | OK | ✅ Гол: Иван Петров (Левски) в 23'
2026-04-22 15:03:00 | картон Иван Петров Левски Y 55 | add_card | OK | ✅ Жълт картон: Иван Петров (Левски) в 55'
```
