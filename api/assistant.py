from http.server import BaseHTTPRequestHandler
import json
import os
import requests

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            
            # Get DeepSeek API key from environment
            deepseek_key = os.getenv('DEEPSEEK_API_KEY', '')
            
            # Process the command using DeepSeek API
            result = self.process_command(data['command'], deepseek_key)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
    
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
                {"role": "system", "content": "You are an AI assistant that helps with email management, website development, and deployment."},
                {"role": "user", "content": command}
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        try:
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            content = response.json()['choices'][0]['message']['content']
            
            # Check for deployment commands
            if "deploy" in command.lower():
                return {"response": content, "action": "deploy"}
            elif "email" in command.lower():
                return {"response": content, "action": "email"}
            
            return {"response": content}
            
        except Exception as e:
            return {"response": f"API Error: {str(e)}", "action": "error"}
