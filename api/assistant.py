from http.server import BaseHTTPRequestHandler
import json
import os
import requests

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)
        
        # Get DeepSeek API key from environment
        deepseek_key = os.getenv('sk-51e3d2eb8c92498d9423cfa56cbf1100', '')
        
        # Process the command using DeepSeek API
        result = self.process_command(data['command'], deepseek_key)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode('utf-8'))
    
    def process_command(self, command, api_key):
        """Process user command using DeepSeek API"""
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
                json=payload
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
            return {"error": str(e)}
