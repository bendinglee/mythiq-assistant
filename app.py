from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import random

app = Flask(__name__)
CORS(app)

# Simple AI responses
responses = {
    "greeting": [
        "Hello! I'm your Mythiq Assistant. I can help with games, media, and chat!",
        "Hi there! Ready to create something amazing together?",
        "Welcome! I'm here to help with your creative projects!"
    ],
    "game": [
        "I'd love to help you create a game! What genre interests you?",
        "Great! Let's build an awesome game. What's your vision?",
        "Game development time! What kind of game are you thinking?"
    ],
    "media": [
        "I can help you create media! What would you like to make?",
        "Perfect! Let's create something visual. Describe your idea!",
        "Media creation is my specialty! What's your concept?"
    ],
    "default": [
        "That's interesting! Tell me more about what you'd like to create.",
        "I'm here to help! What can I assist you with today?",
        "How can I help you bring your ideas to life?"
    ]
}

def get_response_type(message):
    """Simple keyword-based routing"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ["hello", "hi", "hey", "greetings"]):
        return "greeting"
    elif any(word in message_lower for word in ["game", "play", "level", "platformer", "puzzle"]):
        return "game"
    elif any(word in message_lower for word in ["image", "video", "create", "generate", "media"]):
        return "media"
    else:
        return "default"

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "service": "mythiq-assistant",
        "version": "1.0.0",
        "features": ["chat", "game_routing", "media_routing"]
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        if not message:
            return jsonify({
                "response": "I didn't receive a message. How can I help you?",
                "type": "error",
                "confidence": 0.5,
                "status": "error"
            }), 400
        
        # Get response type and generate response
        response_type = get_response_type(message)
        response_text = random.choice(responses[response_type])
        
        return jsonify({
            "response": response_text,
            "type": response_type,
            "confidence": 0.9,
            "status": "success",
            "original_message": message
        })
    
    except Exception as e:
        return jsonify({
            "response": "I'm having some trouble, but I'm still here to help!",
            "type": "error",
            "confidence": 0.5,
            "status": "error",
            "error": str(e)
        }), 500

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "Mythiq Assistant API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "chat": "/api/chat (POST)"
        },
        "status": "running"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    print(f"Starting Mythiq Assistant on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
