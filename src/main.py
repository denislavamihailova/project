from pathlib import Path
from db import execute_script
from chatbot import parse_command, handle_intent
from datetime import datetime

# --- 1️⃣ Зареждаме schema.sql ---
BASE_DIR = Path(__file__).resolve().parent
SCHEMA_PATH = BASE_DIR.parent / "sql" / "schema.sql"

with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
    schema = f.read()

# --- 2️⃣ Създаваме таблиците (clubs + players) ---
execute_script(schema)
print("✅ Таблиците са създадени (clubs + players)")

# --- 3️⃣ Функция за логване ---
def log_command(user_input, response):
    with open("commands.log", "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} | {user_input} | {response}\n")

# --- 4️⃣ Chat loop ---
def main():
    print("⚽ Football AI Assistant стартира!")
    print("Напиши 'помощ' за команди.\n")

    while True:
        user_input = input(">> ")

        intent, param = parse_command(user_input)
        response = handle_intent(intent, param)

        print(response)
        log_command(user_input, response)

        if intent == "exit":
            break

if __name__ == "__main__":
    main()