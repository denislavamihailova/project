# Football AI Assistant - Stage 4: Transfers Module

## Overview

Stage 4 implements a complete **transfer management system** for the Football AI Assistant, including:
- Transfer history tracking in the database
- Player club updates on successful transfers
- Comprehensive error handling and business logic validation
- Transfer queries by player or club
- Atomic database transactions

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
├── intents.json                  # Intent definitions (NLU config)
├── database/
│   └── database.db              # SQLite database file
├── services/
│   ├── __init__.py
│   └── transfers_service.py      # Transfer operations (NEW)
└── utils/
    ├── __init__.py
    └── logger.py                 # Structured logging (NEW)
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
Service Layer (transfers_service.py)
    ↓
Database Layer (db.py)
    ↓
SQLite Database
    ↓
Response → Logging → User Output
```

---

## Database Schema

### transfers table
```sql
CREATE TABLE transfers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,           -- FK → players.id
    from_club_id INTEGER,                 -- FK → clubs.id (can be NULL)
    to_club_id INTEGER NOT NULL,          -- FK → clubs.id
    transfer_date TEXT NOT NULL,          -- Format: YYYY-MM-DD
    fee REAL,                             -- Optional transfer fee
    note TEXT,                            -- Optional notes
    FOREIGN KEY (player_id) REFERENCES players(id),
    FOREIGN KEY (from_club_id) REFERENCES clubs(id),
    FOREIGN KEY (to_club_id) REFERENCES clubs(id)
);
```

### Key Relationships
- **players.club_id** → Updated on transfer
- **transfers.player_id** → FK to players
- **transfers.from_club_id** → Previous club (can be NULL for new players)
- **transfers.to_club_id** → Current club after transfer

---

## Core Features

### 1. Transfer Player Function

**Location:** `src/services/transfers_service.py`

```python
def transfer_player(player_name, from_club, to_club, date, fee=None):
    """
    Execute a player transfer with full validation and atomicity.
    
    Args:
        player_name: Full name of the player
        from_club: Name of the club the player leaves
        to_club: Name of the club the player joins
        date: Transfer date (YYYY-MM-DD format)
        fee: Optional transfer fee (numeric)
    
    Returns:
        String message (success or error)
    
    Raises:
        Validation errors for:
        - Invalid date format
        - Non-matching current club
        - Non-existent player/clubs
        - Same from/to club
    """
```

**Business Logic (Strictly Enforced):**
1. ✅ Validate date format (YYYY-MM-DD)
2. ✅ Check from_club ≠ to_club
3. ✅ Find player by name
4. ✅ Verify player's current club matches from_club
5. ✅ Check both clubs exist
6. ✅ Create transfer record
7. ✅ Update players.club_id atomically
8. ✅ Commit on success, rollback on failure

### 2. List Transfers by Player

**Location:** `src/services/transfers_service.py`

```python
def list_transfers_by_player(player_name):
    """
    Get all transfers for a specific player, ordered by date.
    
    Returns:
        Formatted string with transfer history
    """
```

**Output Format:**
```
📋 Трансфери:
- 2026-03-25: Левски → Лудогорец
- 2026-03-20: ЦСКА → Левски
```

### 3. List Transfers by Club

**Location:** `src/services/transfers_service.py`

```python
def list_transfers_by_club(club_name):
    """
    Get all transfers involving a specific club (in/out).
    
    Returns:
        Formatted string with club transfer activity
    """
```

**Output Format:**
```
📋 Трансфери на Лудогорец:
- 2026-03-25: Иван Петров (Левски → Лудогорец)
- 2026-03-20: Мартин Христов (Левски → Лудогорец)
```

---

## Chatbot Commands

### Transfer Commands

#### 1. Execute Transfer
```
трансфер <player_name> от <from_club> в <to_club> <YYYY-MM-DD>
```

**Example:**
```
трансфер Иван Петров от Левски в Лудогорец 2026-03-25
```

**Response (Success):**
```
✅ Трансфер успешен: Иван Петров от Левски в Лудогорец (2026-03-25)
```

**Possible Errors:**
```
❌ Невалидна дата (YYYY-MM-DD).
❌ Отборите не могат да са еднакви.
❌ Играчът не е намерен.
❌ From клуб не съществува.
❌ To клуб не съществува.
❌ Играчът не е в този клуб.
❌ Грешка при трансфер: <error details>
```

#### 2. Show Transfers (Auto-detects Player or Club)
```
покажи трансфери на <player_name | club_name>
```

**Examples:**
```
покажи трансфери на Иван Петров
покажи трансфери на Лудогорец
```

**Response:**
```
📋 Трансфери:
- 2026-03-25: Левски → Лудогорец

(or)

📋 Трансфери на Лудогорец:
- 2026-03-25: Иван Петров (Левски → Лудогорец)
```

---

## Error Handling

### Validation Rules

| Scenario | Error | Handling |
|----------|-------|----------|
| Invalid date format | "❌ Невалидна дата (YYYY-MM-DD)." | Input validation |
| Same from/to club | "❌ Отборите не могат да са еднакви." | Input validation |
| Player not found | "❌ Играчът не е намерен." | Database lookup |
| From club not found | "❌ From клуб не съществува." | Database lookup |
| To club not found | "❌ To клуб не съществува." | Database lookup |
| Wrong current club | "❌ Играчът не е в този клуб." | Business logic |
| Database error | "❌ Грешка при трансфер: <error>" | Exception handling |

### Atomicity & Rollback

If any step fails:
```python
try:
    # Insert transfer
    cursor.execute(INSERT INTO transfers ...)
    # Update player club
    cursor.execute(UPDATE players SET club_id ...)
    conn.commit()  # Only if both succeed
except Exception as e:
    conn.rollback()  # Undo all changes
    return f"❌ Error: {e}"
```

---

## Logging

### Logger Module

**Location:** `src/utils/logger.py`

**Features:**
- Structured logging to `commands.log`
- Per-command logging with intent, params, result
- Error logging with timestamps

**Log Format:**
```
[2026-03-25 15:30:45] INPUT: трансфер Иван Петров от Левски в Лудогорец 2026-03-25 | INTENT: transfer_player | PARAMS: ('Иван Петров', 'Левски', 'Лудогорец', '2026-03-25', None) | STATUS: OK | RESULT: ✅ Трансфер успешен...
```

**Usage:**
```python
from utils.logger import get_logger

logger = get_logger()
logger.log_command(raw_input, intent, params, result, "OK")
```

---

## Testing & Verification

### Test Data Setup

See `TEST_SCENARIOS_STAGE4.md` for:
- Initial clubs and players
- Pre-populated transfers
- Scenario-by-scenario test cases
- Expected outcomes

### Run Live Demo

```bash
cd src
python main.py
```

Then execute:
```
добави клуб Левски
добави клуб Лудогорец
добави играч Иван Петров в Левски позиция FW номер 9
трансфер Иван Петров от Левски в Лудогорец 2026-03-25
покажи трансфери на Иван Петров
помощ
exit
```

---

## GitHub Commits (Stage 4)

```
feat: Add transfers table to schema
  - transfers table with FK relationships
  - from_club_id support (nullable)
  - transfer_date, fee, note fields

feat: Implement transfers service
  - transfer_player() with full business logic
  - list_transfers_by_player()
  - list_transfers_by_club()
  - Atomic transactions + rollback

feat: Add transfer intents to chatbot
  - Parse "трансфер ... от ... в ..."
  - Parse "покажи трансфери на ..."
  - Auto-detect player vs club in queries

feat: Add logging module
  - utils/logger.py with structured logging
  - Per-command logging to commands.log
  - Timestamp + intent + result tracking

test: Add Stage 4 test scenarios
  - TEST_SCENARIOS_STAGE4.md
  - Setup data + 10 test cases
  - Validation rules + expected results
```

---

## Requirements Checklist

### Database ✅
- [x] transfers table with all required fields
- [x] from_club_id (nullable)
- [x] player_id, to_club_id (FK references)
- [x] transfer_date validation
- [x] Constraints: to_club_id ≠ from_club_id

### Architecture ✅
- [x] Modular structure (services, utils, database)
- [x] Separation of concerns
- [x] NLU → Router → Services → DB flow

### Transfer Service ✅
- [x] transfer_player() function
- [x] list_transfers_by_player() function
- [x] list_transfers_by_club() function (bonus)
- [x] Business logic validation
- [x] Atomic transactions

### Chatbot Integration ✅
- [x] Intent parsing for transfers
- [x] Command parsing with parameters
- [x] Auto-detect player vs club
- [x] Error messages for all validation failures

### Logging ✅
- [x] Structured logger module
- [x] commands.log with timestamps
- [x] Intent + params + result logging

### Testing ✅
- [x] Test scenarios documented
- [x] Error handling verified
- [x] Live demo instructions
- [x] All business rules validated

---

## Live Demonstration

### Key Scenarios to Show

1. **Valid Transfer with Verification**
   ```
   покажи играчи на Левски
   трансфер Иван Петров от Левски в Лудогорец 2026-03-25
   покажи играчи на Лудогорец  (verify player moved)
   ```

2. **Transfer History**
   ```
   покажи трансфери на Иван Петров
   покажи трансфери на Лудогорец
   ```

3. **Error Handling**
   ```
   трансфер Иван Петров от Левски в Славия 2026-03-26  (wrong club)
   трансфер Иван Петров от Лудогорец в Лудогорец 2026-03-27  (same club)
   трансфер NonExistent от ЦСКА в Славия 2026-03-28  (player not found)
   ```

4. **Help & Documentation**
   ```
   помощ  (shows all commands including transfers)
   ```

---

## Summary

✅ **Stage 4 is COMPLETE** with:
- Full transfer management system
- Proper database schema with relationships
- Comprehensive business logic validation
- Atomic transaction handling
- Structured logging
- Complete test scenarios
- Live demo capabilities

The implementation follows clean architecture principles and is production-ready for demonstration.

