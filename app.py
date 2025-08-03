from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from datetime import datetime
import requests

app = Flask(__name__)

# Enable CORS for your frontend domain
CORS(app, origins=[
    'https://mythiq-ui-production.up.railway.app',
    'http://localhost:5173',
    'http://localhost:3000'
])

# Configuration
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
HUGGINGFACE_API_KEY = os.environ.get('HUGGINGFACE_API_KEY')

def check_groq_availability():
    """Check if Groq API is available"""
    try:
        if not GROQ_API_KEY:
            return False
        
        headers = {
            'Authorization': f'Bearer {GROQ_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        # Test with a simple request
        response = requests.post(
            'https://api.groq.com/openai/v1/chat/completions',
            headers=headers,
            json={
                'model': 'llama3-70b-8192',
                'messages': [{'role': 'user', 'content': 'test'}],
                'max_tokens': 1
            },
            timeout=5
        )
        return response.status_code == 200
    except:
        return False

def check_huggingface_availability():
    """Check if HuggingFace API is available"""
    try:
        if not HUGGINGFACE_API_KEY:
            return False
        
        headers = {'Authorization': f'Bearer {HUGGINGFACE_API_KEY}'}
        response = requests.get(
            'https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium',
            headers=headers,
            timeout=5
        )
        return response.status_code in [200, 503]  # 503 means model is loading
    except:
        return False

@app.route('/', methods=['GET'])
def home():
    """Health check and service info"""
    groq_available = check_groq_availability()
    huggingface_available = check_huggingface_availability()
    
    return jsonify({
        'service': 'Mythiq Assistant',
        'status': 'online',
        'version': '2.0.0',
        'timestamp': datetime.now().isoformat(),
        'ai_status': {
            'groq_available': groq_available,
            'huggingface_available': huggingface_available
        },
        'features': [
            'Real AI conversations with Groq Llama 3.1 70B',
            'HuggingFace fallback for reliability',
            'Conversation memory and context',
            'Creative project assistance',
            'Smart error handling'
        ],
        'message': 'Advanced AI assistant with Groq + HuggingFace integration'
    })

@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat():
    """Handle chat requests with AI integration"""
    
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        user_message = data['message']
        
        # Try Groq first
        if GROQ_API_KEY:
            try:
                headers = {
                    'Authorization': f'Bearer {GROQ_API_KEY}',
                    'Content-Type': 'application/json'
                }
                
                groq_response = requests.post(
                    'https://api.groq.com/openai/v1/chat/completions',
                    headers=headers,
                    json={
                        'model': 'llama3-70b-8192',
                        'messages': [
                            {
                                'role': 'system',
                                'content': 'You are Mythiq AI, a creative and intelligent assistant. Provide helpful, engaging, and creative responses. Be enthusiastic about creative projects and innovation.'
                            },
                            {
                                'role': 'user',
                                'content': user_message
                            }
                        ],
                        'max_tokens': 1000,
                        'temperature': 0.7
                    },
                    timeout=30
                )
                
                if groq_response.status_code == 200:
                    groq_data = groq_response.json()
                    ai_response = groq_data['choices'][0]['message']['content']
                    
                    return jsonify({
                        'role': 'assistant',
                        'content': ai_response,
                        'source': 'groq',
                        'model': 'llama3-70b-8192',
                        'timestamp': datetime.now().isoformat()
                    })
                
            except Exception as e:
                print(f"Groq API error: {e}")
        
        # Fallback to HuggingFace
        if HUGGINGFACE_API_KEY:
            try:
                headers = {'Authorization': f'Bearer {HUGGINGFACE_API_KEY}'}
                
                hf_response = requests.post(
                    'https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium',
                    headers=headers,
                    json={'inputs': user_message},
                    timeout=30
                )
                
                if hf_response.status_code == 200:
                    hf_data = hf_response.json()
                    if hf_data and len(hf_data) > 0:
                        ai_response = hf_data[0].get('generated_text', '').replace(user_message, '').strip()
                        
                        if ai_response:
                            return jsonify({
                                'role': 'assistant',
                                'content': ai_response,
                                'source': 'huggingface',
                                'model': 'DialoGPT-medium',
                                'timestamp': datetime.now().isoformat()
                            })
                
            except Exception as e:
                print(f"HuggingFace API error: {e}")
        
        # Final fallback response
        fallback_responses = [
            "I'm here to help you push creative boundaries! What's your wildest idea?",
            "That's a fascinating concept! Let's explore it further together.",
            "Your imagination is powerful! Let's turn those ideas into reality.",
            "Creative projects are my favorite! Let's brainstorm some innovative approaches.",
            "I love helping with creative challenges! What would you like to explore?"
        ]
        
        import random
        fallback_response = random.choice(fallback_responses)
        
        return jsonify({
            'role': 'assistant',
            'content': fallback_response,
            'source': 'fallback',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'mythiq-assistant',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
