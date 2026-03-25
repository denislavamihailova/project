import sys
sys.path.insert(0, "src")

from src.chatbot import parse_command, handle_intent

# Test the command
user_input = "добави клуб Real Madrid"
print(f"Testing: {user_input}")

intent, param = parse_command(user_input)
print(f"Intent: {intent}")
print(f"Param: {param}")

if intent:
    response = handle_intent(intent, param)
    print(f"Response: {response}")
else:
    print("Intent is None!")

