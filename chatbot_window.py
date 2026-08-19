import tkinter as tk
from chatbot import get_reply

window = tk.Tk()
window.title("NOVA-chatbot")
window.geometry("420x520")
window.configure(bg="#1e1e2e")

# --- Conversation display ---
chat_area = tk.Text(
    window, width=48, height=24, bg="#282a36", fg="#f8f8f2",
    font=("Consolas", 11), wrap="word", state="disabled"
)
chat_area.pack(padx=10, pady=10)


def add_line(text):
    chat_area.configure(state="normal")
    chat_area.insert(tk.END, text + "\n")
    chat_area.configure(state="disabled")
    chat_area.see(tk.END)


def send_message():
    user_text = entry.get().strip()
    if not user_text:
        return
    add_line("You: " + user_text)
    entry.delete(0, tk.END)

    if user_text.lower() == "bye":
        add_line("ChatBot: Goodbye!")
        return

    reply = get_reply(user_text)
    add_line("ChatBot: " + reply)


# --- Entry box + Send button ---
bottom_frame = tk.Frame(window, bg="#1e1e2e")
bottom_frame.pack(padx=10, pady=(0, 10), fill="x")

entry = tk.Entry(bottom_frame, font=("Consolas", 11))
entry.pack(side="left", fill="x", expand=True, ipady=6)
entry.bind("<Return>", lambda event: send_message())

send_button = tk.Button(
    bottom_frame, text="Send", command=send_message,
    bg="#50fa7b", fg="#1e1e2e", font=("Consolas", 10, "bold")
)
send_button.pack(side="right", padx=(6, 0))

add_line("ChatBot: Hi! I am ChatBot. Type a message below (or 'bye' to end).")

window.mainloop()