from pathlib import Path
from db import execute_script
from chatbot import parse_command, handle_intent
from datetime import datetime
import sys
import os

# Set UTF-8 encoding for Windows console
os.system('chcp 65001 > nul')

# Ensure UTF-8 encoding for input/output
if sys.stdout.encoding.lower() != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stdin.encoding.lower() != 'utf-8':
    import io
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')

sys.path.append(str(Path(__file__).resolve().parent))

# --- 1️⃣ Зареждаме schema.sql ---
BASE_DIR = Path(__file__).resolve().parent
SCHEMA_PATH = BASE_DIR.parent / "sql" / "schema.sql"

with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
    schema = f.read()

# --- 2️⃣ Създаваме таблиците (clubs + players) ---
execute_script(schema)
print("✅ Таблиците са създадени (clubs + players + leagues + league_teams + matches)")

# --- 3️⃣ Функция за логване ---
def log_command(user_input, intent, response):
    status = "OK" if not response.startswith("❌") else "ERROR"
    with open("commands.log", "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} | {user_input} | {intent} | {status} | {response}\n")

# --- 4️⃣ Chat loop ---
def main():
    print("⚽ Football AI Assistant стартира!")
    print("Напиши 'помощ' за команди.\n")

    while True:
        user_input = input(">> ")
        
        intent, param = parse_command(user_input)
        response = handle_intent(intent, param)

        print(response)
        log_command(user_input, intent, response)

        if intent == "exit":
            break

if __name__ == "__main__":
    main()