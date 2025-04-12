Termphyrio - SSH GUI by Emphyrio
Termphyrio is a simple yet powerful SSH client built using Python and Tkinter. It allows you to easily connect to remote systems via SSH, run commands, and manage multiple SSH sessions within a graphical interface.
---
Features
- **Connect to remote systems via SSH**
- **Open multiple terminal sessions** with a tabbed interface
- **Easy-to-use GUI** to input credentials and execute commands
- **Option to open a terminal** using your default system terminal (e.g., `cmd.exe` on Windows)
- **SSH session history** with navigation through previous commands
---
Installation
### Clone this repository:
```bash
git clone https://github.com/emphyri0/termphyrio.git
cd termphyrio
```
### Install dependencies:
You need to install Python and the required libraries. You can install them with `pip`:
```bash
pip install -r requirements.txt
```
If you don't have a `requirements.txt`, run this to install the necessary packages:
```bash
pip install paramiko tkinter
```
---
Usage
Run the application:
To start the SSH client GUI:
```bash
python termphyrio.py
```
Connect to an SSH server:
1. Enter the **IP address** of the remote machine in the **"IP"** field.
2. Provide your **username** and **password**.
3. Press the **"➕ Connect"** button to establish an SSH session.
Open a system terminal:
Click the **"🖥️ Open Terminal"** button to open your default terminal (e.g., `cmd` on Windows) and connect to the SSH server using your username and IP.
Manage multiple SSH sessions:
Once connected, each session will appear as a tab.
You can easily switch between different SSH sessions by clicking the tabs.
SSH Command History:
Commands entered in the terminal are saved and can be accessed with the **Up** and **Down** arrow keys.
---
Controls
- **Arrow keys (Up/Down)**: Navigate through command history.
- **Return (Enter)**: Send the entered command to the SSH server.
---
Configuration
Your SSH session information (IP and username) is stored in a file located at:
```bash
~/.termphyrio/sessions.json
```You can manually edit this file or use it to retrieve previously used connections.


