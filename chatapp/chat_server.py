#!/usr/bin/env python3
"""
Simple HTTP Chat Server - NO EXTERNAL DEPENDENCIES
Run: python chat_server.py
Then open: http://localhost:8000
Other devices: http://YOUR-IP:8000
"""

import http.server
import socketserver
import threading
import json
import time
from datetime import datetime
from urllib.parse import parse_qs, urlparse
import socket

# Global chat storage
messages = []
connected_clients = []

class ChatHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        """Serve the chat interface"""
        if self.path == '/':
            # Serve HTML page
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = self.get_html()
            self.wfile.write(html.encode())
            
        elif self.path == '/messages':
            # Return all messages as JSON
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = json.dumps(messages)
            self.wfile.write(response.encode())
            
        elif self.path.startswith('/poll'):
            # Long polling for new messages
            last_id = int(self.path.split('?last_id=')[1]) if '?last_id=' in self.path else -1
            
            # Wait for new messages (timeout after 30 seconds)
            start_time = time.time()
            while time.time() - start_time < 30:
                if messages and messages[-1]['id'] > last_id:
                    break
                time.sleep(0.5)
            
            # Return only new messages
            new_messages = [m for m in messages if m['id'] > last_id]
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = json.dumps(new_messages)
            self.wfile.write(response.encode())
            
        else:
            self.send_error(404, "File not found")
    
    def do_POST(self):
        """Handle message submission"""
        if self.path == '/send':
            # Get the message data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            try:
                data = json.loads(post_data)
                user = data.get('user', 'Anonymous')
                text = data.get('text', '')
                
                if text.strip():
                    # Add message to storage
                    msg_id = len(messages)
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    date = datetime.now().strftime("%Y-%m-%d")
                    
                    message = {
                        'id': msg_id,
                        'user': user,
                        'text': text,
                        'time': timestamp,
                        'date': date
                    }
                    
                    messages.append(message)
                    print(f"[{timestamp}] {user}: {text}")
                    
                    # Send response
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    response = json.dumps({'status': 'ok', 'id': msg_id})
                    self.wfile.write(response.encode())
                else:
                    self.send_error(400, "Empty message")
                    
            except Exception as e:
                self.send_error(400, f"Bad request: {str(e)}")
                
        else:
            self.send_error(404, "Not found")
    
    def get_html(self):
        """Return the HTML chat interface"""
        return f'''<!DOCTYPE html>
<html>
<head>
    <title>Simple Chat</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: Arial, sans-serif; 
            background: #f0f0f0;
            padding: 20px;
            height: 100vh;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            height: calc(100vh - 40px);
            display: flex;
            flex-direction: column;
        }}
        header {{
            background: #4CAF50;
            color: white;
            padding: 20px;
            border-radius: 10px 10px 0 0;
        }}
        h1 {{ margin-bottom: 10px; }}
        .status {{
            padding: 5px 10px;
            background: rgba(255,255,255,0.2);
            border-radius: 3px;
            display: inline-block;
        }}
        .chat-area {{
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            border-bottom: 1px solid #eee;
        }}
        .message {{
            margin-bottom: 15px;
            padding: 10px 15px;
            background: #f9f9f9;
            border-radius: 5px;
            border-left: 4px solid #4CAF50;
        }}
        .message-header {{
            color: #666;
            font-size: 0.9em;
            margin-bottom: 5px;
        }}
        .message.own {{
            background: #e8f5e9;
            border-left-color: #2e7d32;
        }}
        .input-area {{
            padding: 20px;
            display: flex;
            gap: 10px;
        }}
        input[type="text"] {{
            flex: 1;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
        }}
        button {{
            padding: 12px 24px;
            background: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }}
        button:hover {{ background: #45a049; }}
        .user-info {{
            padding: 15px 20px;
            background: #f9f9f9;
            border-bottom: 1px solid #eee;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .user-info input {{
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 3px;
            width: 200px;
        }}
        .info {{
            padding: 15px 20px;
            background: #e8f5e9;
            color: #2e7d32;
            font-size: 0.9em;
            border-top: 1px solid #c8e6c9;
        }}
        @media (max-width: 600px) {{
            .input-area {{ flex-direction: column; }}
            button {{ width: 100%; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>💬 Simple Python Chat</h1>
            <div class="status">Connected</div>
            <p>Running on: {get_local_ip()}:8000</p>
        </header>
        
        <div class="user-info">
            <label>Your name:</label>
            <input type="text" id="username" value="User">
            <button onclick="updateUsername()">Update</button>
        </div>
        
        <div class="info">
            💡 Share this address with others on your network to chat together!
        </div>
        
        <div class="chat-area" id="chatArea">
            <!-- Messages will appear here -->
        </div>
        
        <div class="input-area">
            <input type="text" id="messageInput" placeholder="Type your message..." autocomplete="off">
            <button onclick="sendMessage()">Send</button>
        </div>
    </div>

    <script>
        let username = "User";
        let lastMessageId = -1;
        
        // Update username from input
        function updateUsername() {{
            const input = document.getElementById('username');
            if (input.value.trim()) {{
                username = input.value.trim();
                alert('Username updated to: ' + username);
            }}
        }}
        
        // Send a message
        function sendMessage() {{
            const input = document.getElementById('messageInput');
            const text = input.value.trim();
            
            if (!text) return;
            
            // Send to server
            fetch('/send', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                }},
                body: JSON.stringify({{
                    user: username,
                    text: text
                }})
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.status === 'ok') {{
                    input.value = '';
                    input.focus();
                }}
            }})
            .catch(error => console.error('Error:', error));
        }}
        
        // Load messages
        function loadMessages() {{
            fetch('/messages')
                .then(response => response.json())
                .then(messages => {{
                    displayMessages(messages);
                    if (messages.length > 0) {{
                        lastMessageId = messages[messages.length - 1].id;
                    }}
                }})
                .catch(error => console.error('Error loading messages:', error));
        }}
        
        // Poll for new messages
        function pollMessages() {{
            fetch(`/poll?last_id=${{lastMessageId}}`)
                .then(response => response.json())
                .then(newMessages => {{
                    if (newMessages.length > 0) {{
                        displayMessages(newMessages);
                        lastMessageId = newMessages[newMessages.length - 1].id;
                    }}
                    // Poll again
                    setTimeout(pollMessages, 1000);
                }})
                .catch(error => {{
                    console.error('Polling error:', error);
                    setTimeout(pollMessages, 5000); // Wait longer on error
                }});
        }}
        
        // Display messages
        function displayMessages(messages) {{
            const chatArea = document.getElementById('chatArea');
            
            messages.forEach(msg => {{
                // Check if message already displayed
                if (document.getElementById(`msg-${{msg.id}}`)) return;
                
                const messageDiv = document.createElement('div');
                messageDiv.id = `msg-${{msg.id}}`;
                messageDiv.className = 'message' + (msg.user === username ? ' own' : '');
                messageDiv.innerHTML = `
                    <div class="message-header">
                        <strong>${{msg.user}}</strong> 
                        <span>at ${{msg.time}} on ${{msg.date}}</span>
                    </div>
                    <div>${{msg.text}}</div>
                `;
                
                chatArea.appendChild(messageDiv);
            }});
            
            // Scroll to bottom
            chatArea.scrollTop = chatArea.scrollHeight;
        }}
        
        // Handle Enter key
        document.getElementById('messageInput').addEventListener('keypress', function(e) {{
            if (e.key === 'Enter') {{
                sendMessage();
            }}
        }});
        
        // Initialize
        window.onload = function() {{
            username = document.getElementById('username').value;
            loadMessages();
            pollMessages(); // Start polling
        }};
    </script>
</body>
</html>'''
    
    def log_message(self, format, *args):
        """Override to disable default logging"""
        pass

def get_local_ip():
    """Get the local IP address of the machine"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def run_server():
    """Start the HTTP server"""
    port = 8000
    local_ip = get_local_ip()
    
    with socketserver.TCPServer(("", port), ChatHandler) as httpd:
        print("\n" + "="*50)
        print("SIMPLE PYTHON CHAT SERVER")
        print("="*50)
        print(f"\n🌐 Server running at:")
        print(f"   Local:  http://localhost:{port}")
        print(f"   Network: http://{local_ip}:{port}")
        print("\n📱 Open the above URLs in your browser")
        print("   Share the network URL with others on the same Wi-Fi")
        print("\n🛑 Press Ctrl+C to stop the server")
        print("="*50 + "\n")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\nServer stopped.")
            httpd.shutdown()

if __name__ == "__main__":
    run_server()