# Football AI Assistant - Stage 5: Leagues Module

## Overview

Stage 5 implements a complete **league management system** for the Football AI Assistant, including:
- League creation and management
- Team addition/removal to leagues
- Round-robin schedule generation
- Match storage in database
- Comprehensive validation and error handling

---

## Architecture

### Module Structure
```
src/
├── chatbot.py                    # Main chatbot logic + NLU parser
├── db.py                         # Database connection + query execution
├── main.py                       # Entry point with UTF-8 encoding
├── clubs_service.py              # Club management operations
├── players_service.py            # Player management operations
├── database/
│   └── database.db              # SQLite database file
├── repositories/
│   ├── __init__.py
│   └── leagues_repo.py          # SQL queries for leagues (NEW)
├── services/
│   ├── __init__.py
│   ├── transfers_service.py      # Transfer operations
│   └── leagues_service.py        # League operations (NEW)
└── utils/
    ├── __init__.py
    └── logger.py                 # Structured logging
```

### Data Flow

```
User Input
    ↓
parse_command() [chatbot.py]
    ↓
Intent Extraction + Parameter Parsing
    ↓
handle_intent() [chatbot.py]
    ↓
Service Layer (leagues_service.py)
    ↓
Repository Layer (leagues_repo.py)
    ↓
Database Layer (db.py)
    ↓
SQLite Database
    ↓
Response → Logging → User Output
```

---

## Database Schema

### leagues table
```sql
CREATE TABLE leagues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    season TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, season)
);
```

### league_teams table
```sql
CREATE TABLE league_teams (
    league_id INTEGER NOT NULL,
    club_id INTEGER NOT NULL,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (league_id, club_id),
    FOREIGN KEY (league_id) REFERENCES leagues(id) ON DELETE CASCADE,
    FOREIGN KEY (club_id) REFERENCES clubs(id) ON DELETE CASCADE
);
```

### matches table
```sql
CREATE TABLE matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    league_id INTEGER NOT NULL,
    round_no INTEGER NOT NULL,
    home_club_id INTEGER NOT NULL,
    away_club_id INTEGER NOT NULL,
    match_date TEXT,
    home_goals INTEGER,
    away_goals INTEGER,
    FOREIGN KEY (league_id) REFERENCES leagues(id) ON DELETE CASCADE,
    FOREIGN KEY (home_club_id) REFERENCES clubs(id),
    FOREIGN KEY (away_club_id) REFERENCES clubs(id),
    CHECK (home_club_id != away_club_id)
);
```

### Key Relationships
- **leagues**: Stores league info with unique name+season
- **league_teams**: Junction table for many-to-many leagues-clubs
- **matches**: Stores generated matches, linked to league

---

## Core Features

### 1. Create League

**Location:** `src/services/leagues_service.py`

```python
def create_league_service(name, season):
    """
    Create a new league with validation.
    
    Args:
        name: League name
        season: Season in YYYY/YYYY format
    
    Returns:
        Success/error message
    """
```

**Business Logic:**
1. ✅ Validate season format (YYYY/YYYY)
2. ✅ Check league doesn't exist
3. ✅ Insert into leagues table

### 2. Add Team to League

**Location:** `src/services/leagues_service.py`

```python
def add_team_to_league_service(club_name, league_name, season):
    """
    Add a club to a league.
    
    Args:
        club_name: Club name
        league_name: League name
        season: Season
    
    Returns:
        Success/error message
    """
```

**Business Logic:**
1. ✅ Check club exists
2. ✅ Check league exists
3. ✅ Check club not already in league
4. ✅ Insert into league_teams

### 3. Show Teams in League

**Location:** `src/services/leagues_service.py`

```python
def show_teams_in_league_service(league_name, season):
    """
    List all teams in a league.
    
    Returns:
        Formatted list of teams
    """
```

### 4. Remove Team from League

**Location:** `src/services/leagues_service.py`

```python
def remove_team_from_league_service(club_name, league_name, season):
    """
    Remove a club from league if no matches generated.
    
    Returns:
        Success/error message
    """
```

**Business Logic:**
1. ✅ Check club and league exist
2. ✅ Check no matches generated (forbid removal if matches exist)
3. ✅ Delete from league_teams

### 5. Generate Schedule

**Location:** `src/services/leagues_service.py`

```python
def generate_schedule_service(league_name, season):
    """
    Generate round-robin schedule for league.
    
    Returns:
        Report with rounds and matches
    """
```

**Business Logic:**
1. ✅ Check league exists
2. ✅ Check at least 4 teams
3. ✅ Check schedule not already generated
4. ✅ Generate round-robin matches
5. ✅ Insert into matches table

---

## Round-Robin Algorithm

The schedule generation uses a **round-robin tournament algorithm**:

### For Even Number of Teams (N even):
- Rounds = N - 1
- Total matches = N*(N-1)/2
- Each team plays every other team once

### For Odd Number of Teams (N odd):
- Add a "BYE" (rest) team
- Rounds = N
- In each round, (N-1)/2 matches + 1 team rests
- Total matches = N*(N-1)/2

### Implementation Details:
1. Teams are rotated each round
2. Home/away alternates
3. No team plays itself
4. Each team plays once per round

**Example for 4 teams (A,B,C,D):**
```
Round 1: A vs D, B vs C
Round 2: A vs C, D vs B  
Round 3: A vs B, C vs D
```

---

## Chatbot Commands

### League Commands

#### 1. Create League
```
създай лига <name> <season>
```

**Example:**
```
създай лига Първа лига 2025/2026
```

**Response (Success):**
```
✅ Лигата 'Първа лига' за сезон '2025/2026' е създадена с ID 1.
```

**Errors:**
```
❌ Невалиден формат на сезона. Използвай YYYY/YYYY (напр. 2025/2026).
❌ Лигата 'Първа лига' за сезон '2025/2026' вече съществува.
```

#### 2. Add Team to League
```
добави отбор <club> в лига <league> <season>
```

**Example:**
```
добави отбор Левски в лига Първа лига 2025/2026
```

**Response:**
```
✅ Клубът 'Левски' е добавен в лигата 'Първа лига' 2025/2026.
```

#### 3. Show Teams in League
```
покажи отбори в лига <league> <season>
```

**Example:**
```
покажи отбори в лига Първа лига 2025/2026
```

**Response:**
```
📋 Отбори в лигата 'Първа лига' 2025/2026:
- 1: Левски
- 2: ЦСКА
- 3: Лудогорец
- 4: Славия
```

#### 4. Remove Team from League
```
премахни отбор <club> от лига <league> <season>
```

**Example:**
```
премахни отбор Левски от лига Първа лига 2025/2026
```

**Response:**
```
✅ Клубът 'Левски' е премахнат от лигата 'Първа лига' 2025/2026.
```

**Error if matches exist:**
```
❌ Не може да премахнеш отбор, ако има генерирана програма. Изтрий програмата първо.
```

#### 5. Generate Schedule
```
генерирай програма <league> <season>
```

**Example:**
```
генерирай програма Първа лига 2025/2026
```

**Response:**
```
✅ Програма за 'Първа лига' 2025/2026 е генерирана.
Кръгове: 3
Общо мачове: 6
Примерен 1-ви кръг:
- Левски vs ЦСКА
- Лудогорец vs Славия
```

---

## Error Handling

### Validation Rules

| Scenario | Error | Handling |
|----------|-------|----------|
| Invalid season format | "❌ Невалиден формат на сезона..." | Regex validation |
| League exists | "❌ Лигата ... вече съществува." | DB check |
| Club not found | "❌ Клубът ... не съществува." | DB lookup |
| League not found | "❌ Няма лига с име ... сезон ..." | DB lookup |
| Club already in league | "❌ Клубът ... вече е добавен в лигата." | DB check |
| <4 teams for schedule | "❌ Недостатъчно отбори за програма (минимум 4)." | Count check |
| Schedule already generated | "❌ Програмата вече е генерирана..." | DB check |
| Remove with matches | "❌ Не може да премахнеш отбор, ако има генерирана програма." | DB check |

---

## Logging

### commands.log Format
```
datetime | user_input | intent | status | response
```

**Example:**
```
2026-04-01 10:00:00 | създай лига Първа лига 2025/2026 | create_league | OK | ✅ Лигата 'Първа лига' за сезон '2025/2026' е създадена с ID 1.
```

---

## Testing & Verification

### Test Scenarios

See `TEST_SCENARIOS_STAGE5.md` for detailed test cases.

### Run Live Demo

```bash
cd src
python main.py
```

Then execute:
```
добави клуб Левски
добави клуб ЦСКА
добави клуб Лудогорец
добави клуб Славия
създай лига Първа лига 2025/2026
добави отбор Левски в лига Първа лига 2025/2026
добави отбор ЦСКА в лига Първа лига 2025/2026
добави отбор Лудогорец в лига Първа лига 2025/2026
добави отбор Славия в лига Първа лига 2025/2026
покажи отбори в лига Първа лига 2025/2026
генерирай програма Първа лига 2025/2026
помощ
exit
```

---

## Example Dialog

```
⚽ Football AI Assistant стартира!
Напиши 'помощ' за команди.

>> добави клуб Левски
✅ Клубът 'Левски' е добавен успешно.

>> добави клуб ЦСКА
✅ Клубът 'ЦСКА' е добавен успешно.

>> добави клуб Лудогорец
✅ Клубът 'Лудогорец' е добавен успешно.

>> добави клуб Славия
✅ Клубът 'Славия' е добавен успешно.

>> създай лига Първа лига 2025/2026
✅ Лигата 'Първа лига' за сезон '2025/2026' е създадена с ID 1.

>> добави отбор Левски в лига Първа лига 2025/2026
✅ Клубът 'Левски' е добавен в лигата 'Първа лига' 2025/2026.

>> добави отбор ЦСКА в лига Първа лига 2025/2026
✅ Клубът 'ЦСКА' е добавен в лигата 'Първа лига' 2025/2026.

>> добави отбор Лудогорец в лига Първа лига 2025/2026
✅ Клубът 'Лудогорец' е добавен в лигата 'Първа лига' 2025/2026.

>> добави отбор Славия в лига Първа лига 2025/2026
✅ Клубът 'Славия' е добавен в лигата 'Първа лига' 2025/2026.

>> покажи отбори в лига Първа лига 2025/2026
📋 Отбори в лигата 'Първа лига' 2025/2026:
- 1: Левски
- 2: ЦСКА
- 3: Лудогорец
- 4: Славия

>> генерирай програма Първа лига 2025/2026
✅ Програма за 'Първа лига' 2025/2026 е генерирана.
Кръгове: 3
Общо мачове: 6
Примерен 1-ви кръг:
- Левски vs Славия
- ЦСКА vs Лудогорец

>> помощ
📋 Достъпни команди:
--- Клубове ---
- добави клуб <име>
- покажи всички клубове
- изтрий клуб <име>
--- Играчи ---
- добави играч <име> в <клуб> позиция <GK|DF|MF|FW> номер <номер>
- покажи играчи на <клуб>
- смени номер на <име> на <номер>
- изтрий играч <име>
--- Трансфери ---
- трансфер <име играч> от <клуб> в <клуб> <дата YYYY-MM-DD>
- покажи трансфери на <име играч или клуб>
--- Лиги ---
- създай лига <име> <сезон>
- добави отбор <клуб> в лига <име> <сезон>
- премахни отбор <клуб> от лига <име> <сезон>
- покажи отбори в лига <име> <сезон>
- генерирай програма <име> <сезон>
--- Система ---
- помощ / help
- изход / exit

>> изход
⚡ Изход от чатбота. До скоро!
```

---

## Requirements Checklist

### Database ✅
- [x] leagues, league_teams, matches tables
- [x] Proper FK relationships and constraints
- [x] Unique constraints on leagues

### Architecture ✅
- [x] repositories/leagues_repo.py
- [x] services/leagues_service.py
- [x] Modular structure

### League Service ✅
- [x] All CRUD operations
- [x] Round-robin algorithm
- [x] Validation logic

### Chatbot Integration ✅
- [x] Intent parsing for all commands
- [x] Error handling

### Logging ✅
- [x] commands.log with proper format

### Testing ✅
- [x] Test scenarios documented
- [x] Live demo

---

## Summary

✅ **Stage 5 is COMPLETE** with:
- Full league management system
- Round-robin schedule generation
- Proper database schema
- Comprehensive validation
- Clean architecture
- Complete documentation and testing</content>
<parameter name="filePath">C:\Users\Students\PycharmProjects\project\STAGE5_README.md
