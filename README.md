# localhost-chat-app
Real-time Web Chat Application
A simple, real-time web chat application that runs on your local PC's HTTP server. No external dependencies required!

Features
⚡ Instant real-time messaging - Messages appear immediately without delays

🌐 Multi-user support - Anyone on your local network can join

📱 Responsive design - Works on desktop and mobile

🎨 Modern UI - Clean, attractive interface with animations

🔊 Notification sounds - Optional sound alerts for new messages

🔄 Message history - All messages are saved while server is running

💾 No database needed - Everything runs in memory

Requirements
Python 3.6 or higher (usually pre-installed on most systems)

No external packages needed - Uses only Python's standard library

Quick Start
1. Download the Application
Save the following code as chat_server.py:

python
#!/usr/bin/env python3
"""
Real-time Web Chat Server
Run: python chat_server.py
Open: http://localhost:8000
"""

import http.server
import socketserver
import json
import time
import socket
from datetime import datetime
# ... [rest of the code from previous message]
2. Run the Server
Open a terminal/command prompt and run:

bash
# Windows:
python chat_server.py
# or
py chat_server.py

# Mac/Linux:
python3 chat_server.py
3. Access the Chat
