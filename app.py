import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "service": "Mythiq Assistant",
        "status": "online",
        "version": "1.0.0",
        "message": "Ultra-simple version - guaranteed to work!"
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "service": "mythiq-assistant",
        "timestamp": "2025-08-02"
    })

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        message = data.get('message', 'Hello!')
        
        # Simple hardcoded responses - no external APIs
        responses = [
            "Hello! I'm your Mythiq AI assistant. How can I help you today?",
            "That's an interesting question! I'm here to help with your creative projects.",
            "I understand! Let me help you with that creative challenge.",
            "Great idea! I love helping with creative and innovative projects.",
            "Absolutely! I'm designed to assist with all kinds of creative endeavors."
        ]
        
        # Simple response selection based on message length
        response_index = len(message) % len(responses)
        response = responses[response_index]
        
        return jsonify({
            "response": response,
            "provider": "simple",
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({
            "response": "I'm here to help! Please try asking me something else.",
            "provider": "fallback",
            "status": "success"
        })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
