# Stage 5: Leagues - Test Data & Scenarios

## Test Data (Initial Setup)

### Clubs
1. **Левски** (Levski)
2. **ЦСКА** (CSKA)
3. **Лудогорец** (Ludogorets)
4. **Славия** (Slavia)
5. **Ботев** (Botev) - for additional tests

### Leagues
1. **Първа лига** 2025/2026
2. **Втора лига** 2025/2026

## Test Scenarios

### Scenario 1: Create League (SUCCESS)
**Command:** `създай лига Първа лига 2025/2026`
**Expected Result:**
- ✅ League created in database
- ✅ Message: "✅ Лигата 'Първа лига' за сезон '2025/2026' е създадена с ID 1."

**Verification:**
- League exists in leagues table

---

### Scenario 2: Create Duplicate League (FAILURE)
**Command:** `създай лига Първа лига 2025/2026`
**Expected Result:**
- ❌ Rejected
- ❌ Message: "❌ Лигата 'Първа лига' за сезон '2025/2026' вече съществува."

---

### Scenario 3: Invalid Season Format (FAILURE)
**Command:** `създай лига Първа лига 2025-2026`
**Expected Result:**
- ❌ Rejected
- ❌ Message: "❌ Невалиден формат на сезона. Използвай YYYY/YYYY (напр. 2025/2026)."

---

### Scenario 4: Add Team to League (SUCCESS)
**Command:** `добави отбор Левски в лига Първа лига 2025/2026`
**Expected Result:**
- ✅ Team added to league_teams
- ✅ Message: "✅ Клубът 'Левски' е добавен в лигата 'Първа лига' 2025/2026."

---

### Scenario 5: Add Non-existent Club (FAILURE)
**Command:** `добави отбор Несъществуващ в лига Първа лига 2025/2026`
**Expected Result:**
- ❌ Rejected
- ❌ Message: "❌ Клубът 'Несъществуващ' не съществува. Използвай: Покажи всички клубове"

---

### Scenario 6: Add to Non-existent League (FAILURE)
**Command:** `добави отбор Левски в лига Несъществуваща 2025/2026`
**Expected Result:**
- ❌ Rejected
- ❌ Message: "❌ Няма лига с име 'Несъществуваща' сезон '2025/2026'."

---

### Scenario 7: Add Same Team Twice (FAILURE)
**Command:** `добави отбор Левски в лига Първа лига 2025/2026` (after already added)
**Expected Result:**
- ❌ Rejected
- ❌ Message: "❌ Клубът 'Левски' вече е добавен в лигата."

---

### Scenario 8: Show Teams in League (SUCCESS)
**Command:** `покажи отбори в лига Първа лига 2025/2026`
**Expected Result:**
- ✅ List of teams:
  ```
  📋 Отбори в лигата 'Първа лига' 2025/2026:
  - 1: Левски
  - 2: ЦСКА
  - etc.
  ```

---

### Scenario 9: Show Empty League (SUCCESS)
**Command:** `покажи отбори в лига Втора лига 2025/2026`
**Expected Result:**
- ✅ Message: "📋 Лигата 'Втора лига' 2025/2026 няма отбори."

---

### Scenario 10: Remove Team from League (SUCCESS)
**Command:** `премахни отбор Левски от лига Първа лига 2025/2026`
**Expected Result:**
- ✅ Team removed
- ✅ Message: "✅ Клубът 'Левски' е премахнат от лигата 'Първа лига' 2025/2026."

---

### Scenario 11: Generate Schedule with 4 Teams (SUCCESS)
**Prerequisites:** 4 teams added to league
**Command:** `генерирай програма Първа лига 2025/2026`
**Expected Result:**
- ✅ Matches generated
- ✅ Message with rounds, total matches, first round example
- Database has 6 matches (4*3/2)

---

### Scenario 12: Generate Schedule with <4 Teams (FAILURE)
**Prerequisites:** Only 2 teams in league
**Command:** `генерирай програма Първа лига 2025/2026`
**Expected Result:**
- ❌ Rejected
- ❌ Message: "❌ Недостатъчно отбори за програма (минимум 4)."

---

### Scenario 13: Generate Schedule Twice (FAILURE)
**Command:** `генерирай програма Първа лига 2025/2026` (after already generated)
**Expected Result:**
- ❌ Rejected
- ❌ Message: "❌ Програмата вече е генерирана. Изтрий старата програма първо."

---

### Scenario 14: Remove Team After Schedule Generated (FAILURE)
**Prerequisites:** Schedule generated
**Command:** `премахни отбор Левски от лига Първа лига 2025/2026`
**Expected Result:**
- ❌ Rejected
- ❌ Message: "❌ Не може да премахнеш отбор, ако има генерирана програма. Изтрий програмата първо."

---

## Round-Robin Verification

For 4 teams (A,B,C,D), expected matches:
- Round 1: A vs D, B vs C
- Round 2: A vs C, D vs B
- Round 3: A vs B, C vs D

Total: 6 matches, 3 rounds, no duplicates, no self-matches.

## Logging Verification

Each command should log to commands.log with format:
```
datetime | input | intent | OK/ERROR | response
```

Example:
```
2026-04-01 12:00:00 | създай лига Първа лига 2025/2026 | create_league | OK | ✅ Лигата 'Първа лига' за сезон '2025/2026' е създадена с ID 1.
```</content>
<parameter name="filePath">C:\Users\Students\PycharmProjects\project\TEST_SCENARIOS_STAGE5.md
