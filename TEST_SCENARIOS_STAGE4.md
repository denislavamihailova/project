# Stage 4: Transfers - Test Data & Scenarios

## Test Data (Initial Setup)

### Clubs
1. **Левски** (Levski)
2. **Лудогорец** (Ludogorets)
3. **ЦСКА** (CSKA)
4. **Славия** (Slavia)

### Players
1. **Иван Петров** - Левски, FW, №9
2. **Мартин Христов** - Левски, DF, №4
3. **Станислав Иванов** - Лудогорец, MF, №8
4. **Петко Петков** - ЦСКА, GK, №1
5. **Симеон Симеонов** - Славия, FW, №10
6. **Борис Борисов** - ЦСКА, DF, №2

### Initial Transfers
1. 2026-01-15: Борис Борисов: ЦСКА → Славия
2. 2026-02-10: Станислав Иванов: Лудогорец → ЦСКА
3. 2026-03-01: Мартин Христов: Левски → Лудогорец

## Test Scenarios

### Scenario 1: Valid Transfer (SUCCESS)
**Command:** `трансфер Иван Петров от Левски в Лудогорец 2026-03-25`
**Expected Result:** 
- ✅ Transfer recorded in database
- ✅ Player's club_id updated to Лудогорец
- ✅ Message: "✅ Трансфер успешен: Иван Петров от Левски в Лудогорец (2026-03-25)"

**Verification:**
- `покажи играчи на Лудогорец` should show Иван Петров
- `покажи трансфери на Иван Петров` should list the transfer

---

### Scenario 2: Wrong "From" Club (FAILURE)
**Command:** `трансфер Иван Петров от ЦСКА в Славия 2026-03-26`
**Expected Result:**
- ❌ Transfer rejected
- ❌ Message: "❌ Играчът не е в този клуб."
- Database unchanged

**Why it fails:**
- Иван Петров is in Левски (or Лудогорец after scenario 1)
- Attempting to transfer from ЦСКА (wrong club)

---

### Scenario 3: Non-existent Club (FAILURE)
**Command:** `трансфер Иван Петров от Левски в Левски_2 2026-03-27`
**Expected Result:**
- ❌ Transfer rejected
- ❌ Message: "❌ To клуб не съществува."
- Database unchanged

---

### Scenario 4: Same From/To Club (FAILURE)
**Command:** `трансфер Иван Петров от Левски в Левски 2026-03-28`
**Expected Result:**
- ❌ Transfer rejected
- ❌ Message: "❌ Отборите не могат да са еднакви."

---

### Scenario 5: Invalid Date Format (FAILURE)
**Command:** `трансфер Иван Петров от Левски в Славия 25/03/2026`
**Expected Result:**
- ❌ Transfer rejected
- ❌ Message: "❌ Невалидна дата (YYYY-MM-DD)."

---

### Scenario 6: Non-existent Player (FAILURE)
**Command:** `трансфер Неизвестен Играч от Левски в Славия 2026-03-29`
**Expected Result:**
- ❌ Transfer rejected
- ❌ Message: "❌ Играчът не е намерен."

---

### Scenario 7: Show Player Transfers (SUCCESS)
**Command:** `покажи трансфери на Иван Петров`
**Expected Result:**
- ✅ List of all transfers:
  - 2026-03-25: Левски → Лудогорец
  - (Any other previous transfers if applicable)

---

### Scenario 8: Show Club Transfers (SUCCESS)
**Command:** `покажи трансфери на Левски`
**Expected Result:**
- ✅ List of all transfers involving Левски:
  - 2026-03-25: Иван Петров (Левски → Лудогорец)
  - 2026-03-01: Мартин Христов (Левски → Лудогорец)
  - (Any other transfers to/from Левски)

---

### Scenario 9: List Players After Transfer (SUCCESS)
**Command:** `покажи играчи на Лудогорец`
**Expected Result:**
- ✅ Shows all players at Лудогорец including:
  - Иван Петров | FW | №9 | Лудогорец (after scenario 1)
  - Станислав Иванов | MF | №8 | Лудогорец (original)
  - Мартин Христов | DF | №4 | Лудогорец (from scenario data)

---

### Scenario 10: Cascade Update - Club List (SUCCESS)
**Command:** `покажи всички клубове`
**Expected Result:**
- ✅ Shows all clubs remain unchanged
- Note: Transfers don't add/delete clubs, only update player associations

---

## Business Logic Verification

### Required Checks:
- [x] Transaction Atomicity: Both transfer record + player update succeed or both fail
- [x] Club Existence: Both from_club and to_club must exist
- [x] Player Existence: Player must exist in database
- [x] Current Club Match: Player's current club must match from_club
- [x] Date Validation: Must be in YYYY-MM-DD format
- [x] From ≠ To: Cannot transfer to same club
- [x] Player club_id updated on successful transfer
- [x] Transfer record created with proper relationships (FKs)
- [x] Rollback on failure: No partial updates

---

## Live Demonstration Commands

```bash
# Setup
добави клуб Левски
добави клуб Лудогорец
добави клуб ЦСКА
добави клуб Славия

добави играч Иван Петров в Левски позиция FW номер 9
добави играч Мартин Христов в Левски позиция DF номер 4
добави играч Станислав Иванов в Лудогорец позиция MF номер 8
добави играч Петко Петков в ЦСКА позиция GK номер 1
добави играч Симеон Симеонов в Славия позиция FW номер 10
добави играч Борис Борисов в ЦСКА позиция DF номер 2

# Demo: Valid Transfer
трансфер Иван Петров от Левски в Лудогорец 2026-03-25
покажи играчи на Лудогорец
покажи трансфери на Иван Петров

# Demo: Error Handling
трансфер Иван Петров от Левски в Славия 2026-03-26

# Demo: Club Transfers
покажи трансфери на Лудогорец

# Demo: Help
помощ
```

---

## Expected Outcomes

All scenarios should pass with:
- ✅ Correct error messages for failed transfers
- ✅ Successful transfers updating database atomically
- ✅ Accurate transfer history retrieval
- ✅ Proper logging of all commands
- ✅ No orphaned records on failures

