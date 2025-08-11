import streamlit as st
import requests
import os
import json
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
VERCEL_URL = os.getenv('VERCEL_URL', 'https://your-vercel-app.vercel.app')

# Set page config
st.set_page_config(
    page_title="Personal AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm your personal AI assistant. How can I help you today?"}
    ]

# Sidebar configuration
with st.sidebar:
    st.title("Configuration")
    st.subheader("API Settings")
    
    # API key input
    api_key = st.text_input("DeepSeek API Key", value=DEEPSEEK_API_KEY, type="password")
    vercel_url = st.text_input("Vercel API URL", value=VERCEL_URL)
    
    # Feature buttons
    st.subheader("Quick Actions")
    if st.button("🛠️ Create Website", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": "Create a professional portfolio website with dark theme"})
    
    if st.button("📧 Compose Email", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": "Compose an email to my team about the project update"})
    
    if st.button("🚀 Deploy Project", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": "Deploy my website to production"})
    
    # Status indicators
    st.divider()
    st.subheader("System Status")
    status_cols = st.columns(2)
    status_cols[0].metric("AI Status", "Online" if api_key else "Offline")
    status_cols[1].metric("Vercel", "Connected" if vercel_url else "Offline")

# Main chat interface
st.title("🤖 Personal AI Assistant")
st.caption("Powered by DeepSeek AI - Manage emails, deploy websites, and automate tasks")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle user input
if prompt := st.chat_input("What do you want me to do?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Display assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Simulate processing
        with st.spinner("Thinking..."):
            # Send request to Vercel API
            try:
                response = requests.post(
                    f"{vercel_url}/api/assistant",
                    json={"command": prompt},
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if 'response' in result:
                        full_response = result['response']
                        
                        # Special handling for deployment commands
                        if result.get('action') == 'deploy':
                            st.success("Deployment initiated!")
                            st.balloons()
                    else:
                        full_response = f"Error: {result.get('error', 'Unknown error')}"
                else:
                    full_response = f"API error: {response.status_code} - {response.text}"
                
            except Exception as e:
                full_response = f"Connection error: {str(e)}"
        
        # Display response
        message_placeholder.markdown(full_response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})
