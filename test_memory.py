from app.services.memory_llm import chat

session = "dev-session-1"

print("Turn 1:")
print(chat("My function crashes when the input is None. Here it is:\ndef double(x):\n    return x * 2", session))

print("\nTurn 2:")
print(chat("How would I add input validation to fix that?", session))

print("\nTurn 3:")
print(chat("Can you show me the corrected full function?", session))