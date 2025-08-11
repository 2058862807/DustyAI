from http.server import BaseHTTPRequestHandler
import json
import os
import requests
import time

class handler(BaseHTTPRequestHandler):
    def set_headers(self, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_OPTIONS(self):
        self.set_headers(200)
    
    def do_GET(self):
        # Simple health check endpoint
        if self.path == '/api/health':
            self.set_headers(200)
            self.wfile.write(json.dumps(
                {"status": "ok", "time": time.time()}
            ).encode('utf-8'))
        else:
            self.set_headers(404)
            self.wfile.write(json.dumps(
                {"error": "Not found", "path": self.path}
            ).encode('utf-8'))
    
    def do_POST(self):
        try:
            # Handle CORS preflight
            if self.path != '/api/assistant':
                self.set_headers(404)
                self.wfile.write(json.dumps(
                    {"error": "Invalid endpoint"}
                ).encode('utf-8'))
                return
                
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.set_headers(400)
                self.wfile.write(json.dumps(
                    {"error": "Empty request body"}
                ).encode('utf-8'))
                return
                
            # Read and parse request data
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            
            # Validate request structure
            if 'command' not in data:
                self.set_headers(400)
                self.wfile.write(json.dumps(
                    {"error": "Missing 'command' field"}
                ).encode('utf-8'))
                return
                
            # Get DeepSeek API key from environment
            deepseek_key = os.getenv('DEEPSEEK_API_KEY', '')
            
            # Process the command
            result = self.process_command(data['command'], deepseek_key)
            
            # Return successful response
            self.set_headers(200)
            self.wfile.write(json.dumps(result).encode('utf-8'))
            
        except json.JSONDecodeError:
            self.set_headers(400)
            self.wfile.write(json.dumps(
                {"error": "Invalid JSON format"}
            ).encode('utf-8'))
        except Exception as e:
            self.set_headers(500)
            self.wfile.write(json.dumps(
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
            processing_time = time.time() - start_time
            
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
                
            # Add performance metrics
            result["metrics"] = {
                "processing_time": round(processing_time, 2),
                "tokens_used": response.json()['usage']['total_tokens']
            }
            
            return result
            
        except requests.exceptions.Timeout:
            return {"response": "DeepSeek API timed out. Please try again.", "action": "error"}
        except requests.exceptions.RequestException as e:
            return {"response": f"API connection error: {str(e)}", "action": "error"}
        except Exception as e:
            return {"response": f"Processing error: {str(e)}", "action": "error"}
