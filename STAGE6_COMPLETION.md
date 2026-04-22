# Football AI Assistant - Stage 6: Matches Module - COMPLETION

## Overview

Stage 6 implements a complete **matches management system** for the Football AI Assistant, including:
- Match result recording
- Goal and card event tracking
- Match selection and event viewing
- Comprehensive validation and error handling
- Logging of all match operations

---

## Architecture

### Module Structure
```
src/
├── chatbot.py                    # Updated with match commands
├── db.py                         # Database connection
├── main.py                       # Entry point
├── repositories/
│   ├── matches_repo.py           # SQL queries for matches/goals/cards (NEW)
│   └── leagues_repo.py           # Existing
├── services/
│   ├── matches_service.py        # Match operations (NEW)
│   └── leagues_service.py        # Existing
└── database/
    └── database.db               # Updated with goals/cards tables
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
Service Layer (matches_service.py)
    ↓
Repository Layer (matches_repo.py)
    ↓
Database Layer (db.py)
    ↓
SQLite Database
    ↓
Response → Logging → User Output
```

---

## Database Schema Updates

### matches table (updated)
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
    status TEXT DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'played')),
    FOREIGN KEY (league_id) REFERENCES leagues(id) ON DELETE CASCADE,
    FOREIGN KEY (home_club_id) REFERENCES clubs(id),
    FOREIGN KEY (away_club_id) REFERENCES clubs(id),
    CHECK (home_club_id != away_club_id)
);
```

### goals table (new)
```sql
CREATE TABLE goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    club_id INTEGER NOT NULL,
    minute INTEGER NOT NULL CHECK (minute >= 1 AND minute <= 120),
    is_own_goal INTEGER DEFAULT 0 CHECK (is_own_goal IN (0, 1)),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (match_id) REFERENCES matches(id) ON DELETE CASCADE,
    FOREIGN KEY (player_id) REFERENCES players(id),
    FOREIGN KEY (club_id) REFERENCES clubs(id)
);
```

### cards table (new)
```sql
CREATE TABLE cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    club_id INTEGER NOT NULL,
    minute INTEGER NOT NULL CHECK (minute >= 1 AND minute <= 120),
    card_type TEXT NOT NULL CHECK (card_type IN ('Y', 'R')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (match_id) REFERENCES matches(id) ON DELETE CASCADE,
    FOREIGN KEY (player_id) REFERENCES players(id),
    FOREIGN KEY (club_id) REFERENCES clubs(id)
);
```

---

## Core Features

### 1. Show Round Schedule

**Location:** `src/services/matches_service.py`

```python
def show_round_schedule(league_name, season, round_no):
    """
    Display matches for a specific round in a league.
    
    Returns:
        Formatted list of matches with scores/status
    """
```

**Business Logic:**
1. ✅ Validate league exists
2. ✅ Query matches by league and round
3. ✅ Format response with match IDs, teams, scores, status

### 2. Record Match Score

**Location:** `src/services/matches_service.py`

```python
def record_match_score(home_club, away_club, home_goals, away_goals):
    """
    Record the final score for a match.
    
    Args:
        home_club, away_club: Club names
        home_goals, away_goals: Scores
    
    Returns:
        Success/error message
    """
```

**Business Logic:**
1. ✅ Find unique match between teams
2. ✅ Validate match not already played
3. ✅ Validate score format
4. ✅ Update matches table + set status to 'played'

### 3. Add Goal

**Location:** `src/services/matches_service.py`

```python
def add_goal(player_name, club_name, minute):
    """
    Record a goal in the current match.
    
    Args:
        player_name, club_name: Player details
        minute: Goal minute (1-120)
    
    Returns:
        Success/error message
    """
```

**Business Logic:**
1. ✅ Check current match selected
2. ✅ Validate minute (1-120)
3. ✅ Validate player exists in club
4. ✅ Validate club participates in match
5. ✅ Insert into goals table

### 4. Add Card

**Location:** `src/services/matches_service.py`

```python
def add_card(player_name, club_name, card_type, minute):
    """
    Record a card in the current match.
    
    Args:
        player_name, club_name: Player details
        card_type: 'Y' or 'R'
        minute: Card minute (1-120)
    
    Returns:
        Success/error message
    """
```

**Business Logic:**
1. ✅ Check current match selected
2. ✅ Validate card_type ('Y'/'R')
3. ✅ Validate minute (1-120)
4. ✅ Validate player exists in club
5. ✅ Validate club participates in match
6. ✅ Insert into cards table

### 5. Select Current Match

**Location:** `src/services/matches_service.py`

```python
def set_current_match(match_id):
    """
    Set the current match for goal/card operations.
    
    Args:
        match_id: Match ID
    
    Returns:
        Success/error message
    """
```

**Business Logic:**
1. ✅ Validate match exists
2. ✅ Set global current_match_id
3. ✅ Return confirmation with match details

### 6. Show Match Events

**Location:** `src/services/matches_service.py`

```python
def show_match_events(match_id=None):
    """
    Display goals and cards for a match, sorted by minute.
    
    Args:
        match_id: Optional, uses current if None
    
    Returns:
        Chronological list of events
    """
```

**Business Logic:**
1. ✅ Use current match if none specified
2. ✅ Query goals and cards
3. ✅ Sort events by minute
4. ✅ Format response

---

## Chatbot Commands

### Match Commands

#### 1. Show Round
```
покажи кръг <N> <лига> <сезон>
```

**Example:**
```
покажи кръг 1 Първа лига 2025/2026
```

**Response:**
```
📋 Кръг 1 - Първа лига 2025/2026:
- #1: Левски - ЦСКА 2:1 (played)
- #2: Лудогорец - Славия (scheduled)
```

#### 2. Record Score
```
резултат <Домакин>-<Гост> <X>:<Y> запиши
```

**Example:**
```
резултат Левски-ЦСКА 3:0 запиши
```

**Response:**
```
✅ Записано: Левски–ЦСКА 3:0 (мач #1)
```

#### 3. Select Match
```
избери мач <match_id>
```

**Example:**
```
избери мач 1
```

**Response:**
```
✅ Текущият мач е зададен на #1: Левски vs ЦСКА
```

#### 4. Add Goal
```
гол <Играч> <Отбор> <минута> минута
```

**Example:**
```
гол Иван Петров Левски 23 минута
```

**Response:**
```
✅ Гол: Иван Петров (Левски) в 23'
```

#### 5. Add Card
```
картон <Играч> <Отбор> <Y/R> <минута>
```

**Example:**
```
картон Иван Петров Левски Y 55
```

**Response:**
```
✅ Жълт картон: Иван Петров (Левски) в 55'
```

#### 6. Show Events
```
покажи събития [или <match_id>]
```

**Example:**
```
покажи събития
```

**Response:**
```
📋 Събития за мач #1: Левски vs ЦСКА
23': Гол: Иван Петров (Левски)
55': Жълт картон: Иван Петров (Левски)
67': Гол: Петър Стоянов (ЦСКА)
```

---

## Error Handling

### Validation Rules

| Scenario | Error | Handling |
|----------|-------|----------|
| League not found | "❌ Лигата ... не съществува." | DB lookup |
| No matches in round | "❌ Няма мачове за кръг ..." | DB check |
| Match already played | "❌ Резултатът за мач #... вече е записан." | DB check |
| Multiple matches | "❌ Има няколко мача между ..." | Count check |
| Invalid score | "❌ Невалиден резултат..." | Format validation |
| No current match | "❌ Няма избран текущ мач..." | Global check |
| Invalid minute | "❌ Невалидна минута..." | Range check |
| Player not found | "❌ Играч ... не е намерен в клуб ..." | DB lookup |
| Club not in match | "❌ Клубът ... не участва в този мач." | DB check |
| Invalid card type | "❌ Невалиден тип картон..." | Enum check |

---

## Logging

### commands.log Format
```
datetime | user_input | intent | status | response
```

**Example:**
```
2026-04-22 14:30:00 | резултат Левски-ЦСКА 3:0 запиши | record_score | OK | ✅ Записано: Левски–ЦСКА 3:0 (мач #1)
```

---

## Testing & Verification

### Test Scenarios

See `TEST_SCENARIOS_STAGE6.md` for detailed test cases.

### Run Live Demo

```bash
cd src
python main.py
```

Then execute test commands for matches functionality.

---

## Requirements Checklist

### Database ✅
- [x] Updated matches table with status
- [x] goals and cards tables with constraints
- [x] Proper FK relationships

### Architecture ✅
- [x] repositories/matches_repo.py
- [x] services/matches_service.py
- [x] Modular handler → service → repo

### Match Service ✅
- [x] All match operations implemented
- [x] Current match selection
- [x] Comprehensive validations

### Chatbot Integration ✅
- [x] Intent parsing for all commands
- [x] Updated help text

### Logging ✅
- [x] commands.log integration

### Testing ✅
- [x] Error scenarios covered
- [x] Success paths tested

---

## Summary

✅ **Stage 6 is COMPLETE** with:
- Full match management system
- Goal and card event tracking
- Proper validations and error handling
- Clean modular architecture
- Complete logging and documentation
