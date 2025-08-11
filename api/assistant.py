from http.server import BaseHTTPRequestHandler
import json
import os
import requests
import time
import mimetypes

class handler(BaseHTTPRequestHandler):
    def send_response_with_cors(self, status_code, content_type="application/json", body=None):
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        if body:
            self.wfile.write(body)
    
    def do_OPTIONS(self):
        self.send_response_with_cors(200)
    
    def do_GET(self):
        try:
            # Health check endpoint
            if self.path == '/api/health':
                self.send_response_with_cors(200, body=json.dumps(
                    {"status": "ok", "time": time.time()}
                ).encode('utf-8'))
                return
            
            # Serve static files from public directory
            if self.path == '/style.css':
                self.serve_static_file('public/style.css', 'text/css')
                return
            elif self.path == '/script.js':
                self.serve_static_file('public/script.js', 'application/javascript')
                return
            
            # API endpoint not found
            self.send_response_with_cors(404, body=json.dumps(
                {"error": "Not found", "path": self.path}
            ).encode('utf-8'))
            
        except Exception as e:
            self.send_response_with_cors(500, body=json.dumps(
                {"error": f"Internal server error: {str(e)}"}
            ).encode('utf-8'))
    
    def serve_static_file(self, file_path, content_type):
        """Serve a static file with proper content type"""
        if not os.path.exists(file_path):
            self.send_response_with_cors(404, body=b'File not found')
            return
        
        with open(file_path, 'rb') as file:
            self.send_response_with_cors(200, content_type, file.read())
    
    def do_POST(self):
        try:
            if self.path != '/api/assistant':
                self.send_response_with_cors(404, body=json.dumps(
                    {"error": "Invalid endpoint"}
                ).encode('utf-8'))
                return
                
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_response_with_cors(400, body=json.dumps(
                    {"error": "Empty request body"}
                ).encode('utf-8'))
                return
                
            # Read and parse request data
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            
            # Validate request structure
            if 'command' not in data:
                self.send_response_with_cors(400, body=json.dumps(
                    {"error": "Missing 'command' field"}
                ).encode('utf-8'))
                return
                
            # Get DeepSeek API key from environment
            deepseek_key = os.getenv('DEEPSEEK_API_KEY', '')
            
            # Process the command
            result = self.process_command(data['command'], deepseek_key)
            
            # Return successful response
            self.send_response_with_cors(200, body=json.dumps(result).encode('utf-8'))
            
        except json.JSONDecodeError:
            self.send_response_with_cors(400, body=json.dumps(
                {"error": "Invalid JSON format"}
            ).encode('utf-8'))
        except Exception as e:
            self.send_response_with_cors(500, body=json.dumps(
                {"error": f"Internal server error: {str(e)}"}
            ).encode('utf-8'))
    
    def process_command(self, command, api_key):
        """Process user command using DeepSeek API"""
        if not api_key:
            return {"response": "DeepSeek API key not configured", "action": "error"}
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-coder",
            "messages": [
                {
                    "role": "system", 
                    "content": (
                        "You are an AI assistant that helps with email management, "
                        "website development, and deployment. Respond concisely."
                    )
                },
                {
                    "role": "user", 
                    "content": command
                }
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            content = response.json()['choices'][0]['message']['content']
            
            # Format response based on command type
            result = {"response": content}
            
            # Special handling for deployment commands
            if "deploy" in command.lower():
                result["action"] = "deploy"
                result["response"] = f"🚀 Deployment initiated!\n{content}"
                
            # Special handling for email commands
            elif "email" in command.lower():
                result["action"] = "email"
                result["response"] = f"📧 Email prepared!\n{content}"
                
            return result
            
        except requests.exceptions.Timeout:
            return {"response": "DeepSeek API timed out. Please try again.", "action": "error"}
        except requests.exceptions.RequestException as e:
            return {"response": f"API connection error: {str(e)}", "action": "error"}
        except Exception as e:
            return {"response": f"Processing error: {str(e)}", "action": "error"}
