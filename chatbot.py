"""
ChatBot - Terminal version
A rule-based chatbot built following the Applied Agentic AI Month 1 Lab Guide.
"""

import random

# ---- Reply logic (Week 2, Day 11: kept in one clean function) ----

def get_reply(message):
    message = message.lower()

    if "hello" in message or "hi" in message or "hey" in message:
        return random.choice([
            "Hello there!",
            "Hey! Good to see you.",
            "Hi! What's up?"
        ])

    elif "how are you" in message:
        return "I am just code, but I feel great!"

    elif "your name" in message:
        return "I'm ChatBot, your friendly rule-based assistant."

    elif "time" in message:
        return "I can't check a clock yet, but it's always a good time to chat!"

    elif "weather" in message:
        return "I can't check the weather yet, but I hope it's sunny where you are."

    elif "joke" in message:
        return random.choice([
           "Why do Python programmers wear glasses? Because they can't C!",
           "Why did the programmer quit? They lost their domain!",
            "I'd tell you a UDP joke, but you might not get it."
        ])

    elif "food" in message:
        return "I run on electricity, but pizza sounds great for you!"

    elif "help" in message:
        return "You can ask me about the time, jokes, food, weather, or just say hi!"

    elif "what did i say" in message:
        if conversation_log:
            return "You said: " + " | ".join(conversation_log[:-1])
        return "You haven't said anything yet!"

    else:
        return "I am not sure how to answer that yet. Try asking for 'help'."


# ---- Main chat loop (Week 1 + Week 3 memory) ----

conversation_log = []

def main():
    print("Hi! I am ChatBot. What is your name?")
    name = input("You: ")
    print("Nice to meet you, " + name + "! Type 'bye' to leave.")

    message_count = 0

    while True:
        message = input(name + ": ")
        message_lower = message.lower()

        if message_lower == "bye":
            print("ChatBot: Goodbye, " + name + "!")
            break

        conversation_log.append(message)
        message_count += 1

        reply = get_reply(message_lower)
        print("ChatBot: " + reply)

        if message_count == 5:
            print("ChatBot: We've chatted a lot today!")


if __name__ == "__main__":
    main()