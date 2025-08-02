import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# Configuration
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
HUGGINGFACE_API_KEY = os.environ.get('HUGGINGFACE_API_KEY')
AI_PROVIDER = os.environ.get('AI_PROVIDER', 'groq')

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "service": "Mythiq Assistant",
        "status": "online",
        "version": "1.0.0",
        "endpoints": ["/chat", "/health"]
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "service": "mythiq-assistant",
        "groq_configured": bool(GROQ_API_KEY),
        "huggingface_configured": bool(HUGGINGFACE_API_KEY)
    })

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        message = data.get('message', '')
        history = data.get('history', [])
        
        if not message:
            return jsonify({"error": "Message is required"}), 400
        
        # Try Groq first
        if GROQ_API_KEY and AI_PROVIDER in ['groq', 'multi']:
            try:
                response = call_groq_api(message, history)
                return jsonify({"response": response, "provider": "groq"})
            except Exception as e:
                print(f"Groq API error: {e}")
                if AI_PROVIDER == 'groq':
                    return jsonify({"error": "AI service temporarily unavailable"}), 500
        
        # Try Hugging Face as fallback
        if HUGGINGFACE_API_KEY and AI_PROVIDER in ['huggingface', 'multi']:
            try:
                response = call_huggingface_api(message, history)
                return jsonify({"response": response, "provider": "huggingface"})
            except Exception as e:
                print(f"Hugging Face API error: {e}")
        
        # Fallback response
        return jsonify({
            "response": "Hello! I'm your Mythiq AI assistant. I'm currently experiencing some technical difficulties, but I'm here to help with your creative projects!",
            "provider": "fallback"
        })
        
    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({"error": "Internal server error"}), 500

def call_groq_api(message, history):
    """Call Groq API for chat completion"""
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    # Build conversation history
    messages = []
    for msg in history[-5:]:  # Last 5 messages for context
        messages.append({
            "role": msg.get("role", "user"),
            "content": msg.get("content", "")
        })
    
    messages.append({"role": "user", "content": message})
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama-3.1-70b-versatile",
        "messages": messages,
        "max_tokens": 1000,
        "temperature": 0.7
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    
    result = response.json()
    return result["choices"][0]["message"]["content"]

def call_huggingface_api(message, history):
    """Call Hugging Face API for chat completion"""
    url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-large"
    
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Simple prompt for HF
    prompt = f"Human: {message}\nAssistant:"
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_length": 200,
            "temperature": 0.7,
            "do_sample": True
        }
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    
    result = response.json()
    if isinstance(result, list) and len(result) > 0:
        return result[0].get("generated_text", "").replace(prompt, "").strip()
    
    return "I'm here to help with your creative projects!"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
