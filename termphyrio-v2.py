import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import paramiko
import threading
import os
import json
import re

SESSION_FILE = os.path.expanduser("~/.termphyrio/sessions.json")

def strip_ansi(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def load_sessions():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, 'r') as f:
            return json.load(f)
    return []

def save_session(ip, username):
    os.makedirs(os.path.dirname(SESSION_FILE), exist_ok=True)
    sessions = load_sessions()
    entry = {"ip": ip, "username": username}
    if entry not in sessions:
        sessions.append(entry)
        with open(SESSION_FILE, 'w') as f:
            json.dump(sessions, f)

class TermphyrioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Termphyrio - SSH GUI by emphyrio.io")
        self.root.geometry("1000x650")
        self.root.configure(bg="#111111")
        self.sessions = []

        self.control_frame = tk.Frame(root, bg="#111111")
        self.control_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(self.control_frame, text="IP:", fg="white", bg="#111111").grid(row=0, column=0, sticky="w")
        tk.Label(self.control_frame, text="Username:", fg="white", bg="#111111").grid(row=0, column=1, sticky="w")
        tk.Label(self.control_frame, text="Password:", fg="white", bg="#111111").grid(row=0, column=2, sticky="w")

        self.ip_entry = tk.Entry(self.control_frame, width=25, bg="#1a1a1a", fg="white", insertbackground='white')
        self.ip_entry.grid(row=1, column=0, padx=(0, 10), sticky="ew")

        self.username = tk.Entry(self.control_frame, width=15, bg="#1a1a1a", fg="white", insertbackground='white')
        self.username.grid(row=1, column=1, padx=(0, 10))

        self.password = tk.Entry(self.control_frame, width=15, show="*", bg="#1a1a1a", fg="white", insertbackground='white')
        self.password.grid(row=1, column=2, padx=(0, 10))

        self.connect_btn = tk.Button(self.control_frame, text="➕ Connect", command=self.connect,
                                     bg="#222", fg="white", relief=tk.FLAT)
        self.connect_btn.grid(row=1, column=3)

        self.open_terminal_btn = tk.Button(self.control_frame, text="🖥️ Open Terminal", command=self.open_native_terminal,
                                           bg="#333", fg="white", relief=tk.FLAT)
        self.open_terminal_btn.grid(row=1, column=4, padx=(10, 0))

        style = ttk.Style()
        style.theme_use('default')
        style.configure("TNotebook", background="#111111", borderwidth=0)
        style.configure("TNotebook.Tab", background="#1a1a1a", foreground="white", padding=5)
        style.map("TNotebook.Tab", background=[("selected", "#0a0f1a")])

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def connect(self):
        ip = self.ip_entry.get()
        username = self.username.get()
        password = self.password.get()
        if not all([ip, username, password]):
            messagebox.showwarning("Missing Input", "Please fill in IP, username, and password.")
            return
        session = SSHSession(self.notebook, ip, username, password, self._remove_session)
        self.sessions.append(session)

    def open_native_terminal(self):
        ip = self.ip_entry.get()
        username = self.username.get()
        if not ip or not username:
            messagebox.showwarning("Missing Input", "Please enter IP and username to open terminal.")
            return
        try:
            os.system(f'start cmd /k ssh {username}@{ip}')
        except Exception as e:
            messagebox.showerror("Error", f"Could not open native terminal: {e}")

    def _remove_session(self, session):
        self.sessions.remove(session)

class SSHSession:
    def __init__(self, notebook, ip, username, password, close_callback):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.chan = None
        self.ip = ip
        self.close_callback = close_callback

        self.frame = tk.Frame(notebook, bg="#0a0f1a")

        self.output = scrolledtext.ScrolledText(self.frame, wrap=tk.WORD, bg="#0a0f1a", fg="#00ff88",
                                                insertbackground='white', font=("Courier New", 10), borderwidth=0)
        self.output.grid(row=0, column=0, sticky="nsew", padx=0, pady=(0, 0))

        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)

        self.setup_input_bar()

        try:
            self.ssh.connect(ip, username=username, password=password)
            self.chan = self.ssh.invoke_shell()
            threading.Thread(target=self.receive_output, daemon=True).start()
            self.print_output(f"[✅ Connected to {ip} as {username}]\n")
            save_session(ip, username)
        except Exception as e:
            self.print_output(f"[❌ Connection failed: {e}]\n")

        self.tab_id = notebook.index("end")
        notebook.add(self.frame, text=f"{ip} ✖")
        notebook.select(self.tab_id)
        notebook.tab(self.tab_id, compound=tk.LEFT)
        self.notebook = notebook
        self._add_tab_click_close()

    def _add_tab_click_close(self):
        self.notebook.bind("<Button-1>", self._on_click)

    def _on_click(self, event):
        x, y = event.x, event.y
        for index in range(self.notebook.index("end")):
            tab_bbox = self.notebook.bbox(index)
            if tab_bbox and tab_bbox[0] < x < tab_bbox[0] + tab_bbox[2]:
                if x > tab_bbox[0] + tab_bbox[2] - 20:
                    self.close()
                break

    def receive_output(self):
        while True:
            try:
                if self.chan.recv_ready():
                    data = self.chan.recv(4096)
                    text = data.decode(errors='ignore')
                    self.output.after(0, lambda t=text: self.print_output(strip_ansi(t)))
            except Exception as e:
                self.output.after(0, lambda: self.print_output(f"[❌ Receive error: {e}]\n"))
                break

    def setup_input_bar(self):
        self.input_frame = tk.Frame(self.frame, bg="#0a0f1a")
        self.input_frame.grid(row=2, column=0, sticky="ew")

        self.cmd_input = tk.Entry(self.input_frame, bg="#003366", fg="#ffffff", insertbackground='white', relief=tk.FLAT)
        self.cmd_input.pack(fill=tk.X, padx=5, pady=3)
        self.cmd_input.bind("<Return>", self.send_cmd)
        self.cmd_input.bind("<Up>", self.navigate_history_up)
        self.cmd_input.bind("<Down>", self.navigate_history_down)

        self.command_history = []
        self.history_index = -1

    def send_cmd(self, event=None):
        cmd = self.cmd_input.get()
        if self.chan and self.chan.send_ready():
            try:
                self.chan.send(cmd + "\n")
                self.command_history.append(cmd)
                self.history_index = len(self.command_history)
            except Exception as e:
                self.print_output(f"[❌ Send error: {e}]\n")
            self.cmd_input.delete(0, tk.END)

    def navigate_history_up(self, event=None):
        if self.command_history and self.history_index > 0:
            self.history_index -= 1
            self.cmd_input.delete(0, tk.END)
            self.cmd_input.insert(0, self.command_history[self.history_index])

    def navigate_history_down(self, event=None):
        if self.command_history and self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            self.cmd_input.delete(0, tk.END)
            self.cmd_input.insert(0, self.command_history[self.history_index])
        else:
            self.cmd_input.delete(0, tk.END)

    def print_output(self, text):
        self.output.insert(tk.END, text)
        self.output.see(tk.END)

    def close(self):
        try:
            if self.chan:
                self.chan.close()
            if self.ssh:
                self.ssh.close()
        except:
            pass
        self.notebook.forget(self.frame)
        self.close_callback(self)

if __name__ == "__main__":
    root = tk.Tk()
    app = TermphyrioApp(root)
    root.mainloop()
