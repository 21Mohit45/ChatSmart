import socket
import threading
import tkinter as tk
from tkinter import simpledialog, filedialog
import os

HOST = '127.0.0.1'
PORT = 5000

# ---------------- SPLASH SCREEN ----------------
def splash():
    s = tk.Tk()
    s.configure(bg="#075E54")
    s.state("zoomed")  # Full screen
    s.overrideredirect(True)

    # Center Content
    frame = tk.Frame(s, bg="#075E54")
    frame.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(
        frame,
        text="Chat Smart",
        font=("Segoe UI", 60, "bold"),
        bg="#075E54",
        fg="white"
    ).pack()

    tk.Label(
        frame,
        text="Connecting You Smartly...",
        font=("Segoe UI", 18),
        bg="#075E54",
        fg="white"
    ).pack(pady=15)

    tk.Label(
        s,
        text="Created by Mohit Patil"    
        font=("Segoe UI", 16),
        bg="#075E54",
        fg="white"
    ).place(relx=0.5, rely=0.95, anchor="center")

    s.after(2000, s.destroy)
    s.mainloop()

splash()

# ---------------- LOGIN ----------------
login = tk.Tk()
login.withdraw()
username = simpledialog.askstring("Login", "Enter Username")

# ---------------- SOCKET ----------------
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
client.send(username.encode())

selected_user = None
chat_history = {}

# ---------------- RECEIVE ----------------
def receive():
    while True:
        try:
            message = client.recv(1024)

            if message.startswith(b"USERS:"):
                users = message.decode().replace("USERS:", "").split(",")
                user_list.delete(0, tk.END)
                for user in users:
                    if user != username:
                        user_list.insert(tk.END, user)

            elif message.startswith(b"PRIVATE|"):
                _, sender, msg = message.decode().split("|", 2)

                if sender not in chat_history:
                    chat_history[sender] = []

                chat_history[sender].append((sender, msg))
                if selected_user == sender:
                    display_chat(sender)

            elif message.startswith(b"FILE|"):
                header = message.decode().split("|")
                sender = header[1]
                filename = header[2]
                filesize = int(header[3])

                file_data = b""
                while len(file_data) < filesize:
                    file_data += client.recv(1024)

                with open("received_" + filename, "wb") as f:
                    f.write(file_data)

                if sender not in chat_history:
                    chat_history[sender] = []

                chat_history[sender].append((sender, f"📁 File received: {filename}"))
                if selected_user == sender:
                    display_chat(sender)

        except:
            break

# ---------------- SEND MESSAGE ----------------
def send_message(event=None):
    global selected_user
    msg = message_entry.get()

    if selected_user and msg.strip():
        client.send(f"{selected_user}|{msg}".encode())

        if selected_user not in chat_history:
            chat_history[selected_user] = []

        chat_history[selected_user].append(("You", msg))
        display_chat(selected_user)

    message_entry.delete(0, tk.END)

# ---------------- SEND FILE ----------------
def send_file():
    global selected_user

    if not selected_user:
        return

    filepath = filedialog.askopenfilename()
    if not filepath:
        return

    filename = os.path.basename(filepath)
    filesize = os.path.getsize(filepath)

    client.send(f"FILE|{selected_user}|{filename}|{filesize}".encode())

    with open(filepath, "rb") as f:
        client.sendall(f.read())

    if selected_user not in chat_history:
        chat_history[selected_user] = []

    chat_history[selected_user].append(("You", f"📁 File sent: {filename}"))
    display_chat(selected_user)

# ---------------- DISPLAY CHAT ----------------
def display_chat(user):
    for widget in chat_frame.winfo_children():
        widget.destroy()

    for sender, msg in chat_history.get(user, []):
        frame = tk.Frame(chat_frame, bg="#ECE5DD")
        frame.pack(fill="both", pady=5)

        bubble = tk.Label(
            frame,
            text=f"{sender}: {msg}",
            bg="red" if sender == "You" else "#FFFFFF",
            fg="white" if sender == "You" else "black",
            font=("Segoe UI", 11),
            padx=10,
            pady=5
        )

        if sender == "You":
            bubble.pack(anchor="e", padx=15)
        else:
            bubble.pack(anchor="w", padx=15)

# ---------------- SELECT USER ----------------
def select_user(event):
    global selected_user
    selected_user = user_list.get(user_list.curselection())
    display_chat(selected_user)

# ---------------- MAIN UI ----------------
root = tk.Tk()
root.title("Chat Smart")
root.geometry("1000x650")
root.configure(bg="#ECE5DD")

# LEFT PANEL
left = tk.Frame(root, width=250, bg="#075E54")
left.pack(side="left", fill="y")

# Profile Circle
profile_canvas = tk.Canvas(left, width=90, height=90,
                           bg="#075E54", highlightthickness=0)
profile_canvas.pack(pady=20)

profile_canvas.create_oval(15, 15, 75, 75, fill="#25D366")
profile_canvas.create_text(45, 45,
                           text=username[0].upper(),
                           fill="white",
                           font=("Segoe UI", 28, "bold"))

tk.Label(left, text=username,
         bg="#075E54",
         fg="white",
         font=("Segoe UI", 13, "bold")).pack()

tk.Label(left, text="Online Users",
         bg="#075E54",
         fg="white",
         font=("Segoe UI", 13)).pack(pady=15)

user_list = tk.Listbox(left,
                       bg="#128C7E",
                       fg="white",
                       font=("Segoe UI", 12),
                       bd=0)
user_list.pack(fill="both", expand=True, padx=10, pady=10)
user_list.bind("<<ListboxSelect>>", select_user)

# RIGHT PANEL
right = tk.Frame(root, bg="#ECE5DD")
right.pack(side="right", fill="both", expand=True)

canvas = tk.Canvas(right, bg="#ECE5DD", highlightthickness=0)
scrollbar = tk.Scrollbar(right, command=canvas.yview)
chat_frame = tk.Frame(canvas, bg="#ECE5DD")

chat_frame.bind("<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

canvas.create_window((0, 0), window=chat_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# BOTTOM MESSAGE BAR
bottom = tk.Frame(root, bg="white", height=60)
bottom.pack(side="bottom", fill="x")

bottom.columnconfigure(1, weight=1)

file_btn = tk.Button(bottom, text="📁",
                     font=("Segoe UI", 12),
                     width=3,
                     command=send_file)
file_btn.grid(row=0, column=0, padx=10, pady=10)

message_entry = tk.Entry(bottom,
                         font=("Segoe UI", 12),
                         bd=0)
message_entry.grid(row=0, column=1,
                   sticky="ew", padx=5, pady=10)
message_entry.bind("<Return>", send_message)

send_btn = tk.Button(bottom,
                     text="Send",
                     bg="#25D366",
                     fg="white",
                     font=("Segoe UI", 12, "bold"),
                     width=8,
                     command=send_message)
send_btn.grid(row=0, column=2, padx=10, pady=10)

threading.Thread(target=receive, daemon=True).start()
root.mainloop()