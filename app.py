from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
HUGGINGFACE_API_KEY = os.environ.get('HUGGINGFACE_API_KEY')

# Conversation memory (simple in-memory storage)
conversations = {}

class AIAssistant:
    def __init__(self):
        self.groq_available = bool(GROQ_API_KEY)
        self.hf_available = bool(HUGGINGFACE_API_KEY)
        
    def call_groq_api(self, message, conversation_history=[]):
        """Call Groq API for AI responses"""
        if not self.groq_available:
            return None
            
        try:
            # Prepare conversation context
            messages = [
                {"role": "system", "content": "You are Mythiq AI, a creative assistant that helps users with artistic projects, game development, storytelling, and creative problem-solving. Be helpful, creative, and inspiring."}
            ]
            
            # Add conversation history
            for msg in conversation_history[-10:]:  # Keep last 10 messages for context
                messages.append(msg)
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Call Groq API
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            
            data = {
                "messages": messages,
                "model": "llama-3.1-70b-versatile",
                "temperature": 0.7,
                "max_tokens": 1000,
                "stream": False
            }
            
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                logger.error(f"Groq API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Groq API exception: {str(e)}")
            return None
    
    def call_huggingface_api(self, message):
        """Call HuggingFace API as fallback"""
        if not self.hf_available:
            return None
            
        try:
            headers = {
                "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
                "Content-Type": "application/json"
            }
            
            data = {
                "inputs": f"You are Mythiq AI, a creative assistant. User: {message}\nMythiq AI:",
                "parameters": {
                    "max_new_tokens": 500,
                    "temperature": 0.7,
                    "return_full_text": False
                }
            }
            
            response = requests.post(
                "https://api-inference.huggingface.co/models/meta-llama/Llama-2-70b-chat-hf",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get('generated_text', '').strip()
                return None
            else:
                logger.error(f"HuggingFace API error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"HuggingFace API exception: {str(e)}")
            return None
    
    def get_fallback_response(self, message):
        """Creative fallback responses when APIs are unavailable"""
        creative_responses = [
            "I'm here to spark your creativity! What kind of project are you working on?",
            "That's a fascinating idea! Let me help you explore that creative direction.",
            "I love helping with creative challenges! Tell me more about your vision.",
            "Your creativity is inspiring! How can I help bring your ideas to life?",
            "That sounds like an amazing project! What aspects would you like to develop?",
            "I'm excited to help with your creative journey! What's your next step?",
            "Creative projects are my favorite! Let's brainstorm some innovative approaches.",
            "That's a wonderful concept! How can we make it even more engaging?",
            "I'm here to help you push creative boundaries! What's your wildest idea?",
            "Your imagination is powerful! Let's turn those ideas into reality."
        ]
        
        # Simple hash-based selection for consistency
        import hashlib
        hash_val = int(hashlib.md5(message.lower().encode()).hexdigest(), 16)
        return creative_responses[hash_val % len(creative_responses)]
    
    def generate_response(self, message, user_id="default"):
        """Generate AI response with smart fallback system"""
        try:
            # Get conversation history
            history = conversations.get(user_id, [])
            
            # Try Groq first (primary AI)
            response = self.call_groq_api(message, history)
            if response:
                # Update conversation history
                history.append({"role": "user", "content": message})
                history.append({"role": "assistant", "content": response})
                conversations[user_id] = history[-20:]  # Keep last 20 messages
                return response, "groq"
            
            # Try HuggingFace as fallback
            response = self.call_huggingface_api(message)
            if response:
                # Update conversation history
                history.append({"role": "user", "content": message})
                history.append({"role": "assistant", "content": response})
                conversations[user_id] = history[-20:]
                return response, "huggingface"
            
            # Use creative fallback
            response = self.get_fallback_response(message)
            return response, "fallback"
            
        except Exception as e:
            logger.error(f"Response generation error: {str(e)}")
            return "I'm experiencing some technical difficulties, but I'm still here to help with your creative projects!", "error"

# Initialize AI assistant
ai_assistant = AIAssistant()

@app.route('/')
def home():
    """Service status endpoint"""
    return jsonify({
        "service": "Mythiq Assistant",
        "status": "online",
        "version": "2.0.0",
        "message": "Advanced AI assistant with Groq + HuggingFace integration",
        "features": [
            "Real AI conversations with Groq Llama 3.1 70B",
            "HuggingFace fallback for reliability",
            "Conversation memory and context",
            "Creative project assistance",
            "Smart error handling"
        ],
        "ai_status": {
            "groq_available": ai_assistant.groq_available,
            "huggingface_available": ai_assistant.hf_available
        },
        "timestamp": datetime.now().isoformat()
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "service": "mythiq-assistant",
        "status": "healthy",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ai_providers": {
            "groq": "available" if ai_assistant.groq_available else "unavailable",
            "huggingface": "available" if ai_assistant.hf_available else "unavailable"
        }
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"error": "Message is required"}), 400
        
        message = data['message'].strip()
        if not message:
            return jsonify({"error": "Message cannot be empty"}), 400
        
        user_id = data.get('user_id', 'default')
        
        # Generate AI response
        response, provider = ai_assistant.generate_response(message, user_id)
        
        return jsonify({
            "response": response,
            "provider": provider,
            "timestamp": datetime.now().isoformat(),
            "conversation_length": len(conversations.get(user_id, []))
        })
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        return jsonify({
            "error": "I'm experiencing some technical difficulties, but I'm still here to help!",
            "provider": "error"
        }), 500

@app.route('/conversation/<user_id>')
def get_conversation(user_id):
    """Get conversation history"""
    try:
        history = conversations.get(user_id, [])
        return jsonify({
            "conversation": history,
            "length": len(history),
            "user_id": user_id
        })
    except Exception as e:
        logger.error(f"Conversation endpoint error: {str(e)}")
        return jsonify({"error": "Could not retrieve conversation"}), 500

@app.route('/clear/<user_id>', methods=['POST'])
def clear_conversation(user_id):
    """Clear conversation history"""
    try:
        if user_id in conversations:
            del conversations[user_id]
        return jsonify({
            "message": "Conversation cleared",
            "user_id": user_id
        })
    except Exception as e:
        logger.error(f"Clear conversation error: {str(e)}")
        return jsonify({"error": "Could not clear conversation"}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    logger.info(f"Starting Mythiq Assistant on port {port}")
    logger.info(f"Groq API available: {ai_assistant.groq_available}")
    logger.info(f"HuggingFace API available: {ai_assistant.hf_available}")
    
    app.run(host='0.0.0.0', port=port, debug=False)
