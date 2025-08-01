"""
Updated app.py for Mythiq Assistant with Smart Brain + Fallback
Railway-optimized Flask server with graceful fallback
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Try to import smart brain, fallback to simple brain
try:
    from brain_smart_lightweight import SmartLightweightBrain
    brain = SmartLightweightBrain()
    BRAIN_TYPE = "smart_lightweight"
    logger.info("Smart Lightweight Brain loaded successfully!")
except ImportError:
    logger.warning("Smart brain not found, using simple fallback brain")
    
    # Simple fallback brain
    class SimpleFallbackBrain:
        def __init__(self):
            self.conversation_count = 0
            
        def process_message(self, message, user_id=None, session_id=None):
            self.conversation_count += 1
            
            # Simple but intelligent responses
            message_lower = message.lower()
            
            # Game requests
            if any(word in message_lower for word in ["game", "play", "level", "character"]):
                return {
                    'content': "I love that you're interested in game development! 🎮 While I'm running in simple mode right now, I can still help you brainstorm game ideas. What type of game experience are you envisioning?",
                    'intent': 'game_request',
                    'confidence': 0.8,
                    'emotion': {'primary': 'excited', 'intensity': 0.7, 'confidence': 0.8},
                    'context': {'conversation_length': self.conversation_count},
                    'metadata': {'brain_type': 'simple_fallback', 'timestamp': datetime.now().isoformat()}
                }
            
            # Media requests
            elif any(word in message_lower for word in ["image", "video", "create", "media"]):
                return {
                    'content': "Media creation is exciting! 🎨 I'm currently in simple mode, but I can still help you plan your creative projects. What kind of visual content are you looking to create?",
                    'intent': 'media_request',
                    'confidence': 0.8,
                    'emotion': {'primary': 'creative', 'intensity': 0.6, 'confidence': 0.7},
                    'context': {'conversation_length': self.conversation_count},
                    'metadata': {'brain_type': 'simple_fallback', 'timestamp': datetime.now().isoformat()}
                }
            
            # Help requests
            elif any(word in message_lower for word in ["help", "how", "what", "explain"]):
                return {
                    'content': "I'm here to help! 💙 Even in simple mode, I can assist with brainstorming, planning, and guidance. What specific challenge are you working on?",
                    'intent': 'help_request',
                    'confidence': 0.9,
                    'emotion': {'primary': 'helpful', 'intensity': 0.8, 'confidence': 0.9},
                    'context': {'conversation_length': self.conversation_count},
                    'metadata': {'brain_type': 'simple_fallback', 'timestamp': datetime.now().isoformat()}
                }
            
            # Greetings
            elif any(word in message_lower for word in ["hello", "hi", "hey", "greetings"]):
                return {
                    'content': "Hello there! 👋 I'm Mythiq, your AI assistant. I'm currently running in simple mode, but I'm still here to help with your creative projects and ideas. What's on your mind today?",
                    'intent': 'greeting',
                    'confidence': 0.9,
                    'emotion': {'primary': 'friendly', 'intensity': 0.7, 'confidence': 0.8},
                    'context': {'conversation_length': self.conversation_count},
                    'metadata': {'brain_type': 'simple_fallback', 'timestamp': datetime.now().isoformat()}
                }
            
            # Default response
            else:
                return {
                    'content': f"I hear you saying: '{message}'. While I'm in simple mode right now, I'm still a reliable AI assistant ready to help with your creative projects! What would you like to explore together?",
                    'intent': 'chat',
                    'confidence': 0.7,
                    'emotion': {'primary': 'neutral', 'intensity': 0.5, 'confidence': 0.6},
                    'context': {'conversation_length': self.conversation_count},
                    'metadata': {'brain_type': 'simple_fallback', 'timestamp': datetime.now().isoformat()}
                }
        
        def health_check(self):
            return {
                'status': 'healthy',
                'brain_type': 'simple_fallback',
                'message': 'Simple fallback brain operational',
                'note': 'Upload brain_smart_lightweight.py for full AI capabilities',
                'capabilities': {
                    'basic_responses': True,
                    'intent_detection': True,
                    'simple_emotion_analysis': True,
                    'game_routing': True,
                    'media_routing': True,
                    'help_assistance': True
                }
            }
        
        def get_brain_status(self):
            return {
                'status': 'simple_fallback_operational',
                'version': '1.0.0',
                'brain_type': 'simple_fallback',
                'conversation_count': self.conversation_count,
                'note': 'This is a fallback brain. Upload brain_smart_lightweight.py for advanced AI features.',
                'upgrade_instructions': 'Add brain_smart_lightweight.py to your repository for professional-grade AI responses'
            }
    
    brain = SimpleFallbackBrain()
    BRAIN_TYPE = "simple_fallback"

@app.route('/')
def home():
    """API information endpoint"""
    return jsonify({
        "message": "Mythiq Assistant API",
        "version": "2.0.0",
        "brain_type": BRAIN_TYPE,
        "status": "running",
        "endpoints": {
            "chat": "/api/chat (POST)",
            "health": "/health",
            "brain_status": "/brain/status"
        },
        "note": "Upload brain_smart_lightweight.py for full AI capabilities" if BRAIN_TYPE == "simple_fallback" else "Smart brain active!"
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat endpoint with smart brain or fallback"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'error': 'Message is required',
                'status': 'error'
            }), 400
        
        message = data.get('message', '').strip()
        user_id = data.get('user_id', 'default')
        session_id = data.get('session_id', None)
        
        if not message:
            return jsonify({
                'error': 'Message cannot be empty',
                'status': 'error'
            }), 400
        
        logger.info(f"Processing message from user {user_id}: {message[:50]}...")
        
        # Process with brain (smart or fallback)
        response = brain.process_message(message, user_id, session_id)
        
        logger.info(f"Generated response with intent: {response['intent']}, confidence: {response['confidence']:.2f}")
        
        return jsonify({
            'response': response['content'],
            'intent': response['intent'],
            'confidence': response['confidence'],
            'emotion': response['emotion'],
            'context': response['context'],
            'metadata': response['metadata'],
            'brain_type': BRAIN_TYPE,
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return jsonify({
            'response': "I'm experiencing a technical moment, but I'm still here and ready to help! Could you try rephrasing that?",
            'intent': 'error',
            'confidence': 0.5,
            'emotion': {'primary': 'neutral', 'intensity': 0.5, 'confidence': 0.5},
            'brain_type': BRAIN_TYPE,
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/health')
def health():
    """Health check endpoint for Railway"""
    try:
        health_status = brain.health_check()
        health_status['brain_type'] = BRAIN_TYPE
        return jsonify(health_status)
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            'status': 'unhealthy',
            'brain_type': BRAIN_TYPE,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/brain/status')
def brain_status():
    """Detailed brain status and metrics"""
    try:
        if hasattr(brain, 'get_brain_status'):
            status = brain.get_brain_status()
        else:
            status = {
                'status': 'simple_fallback_operational',
                'brain_type': BRAIN_TYPE,
                'note': 'Upload brain_smart_lightweight.py for advanced features'
            }
        return jsonify(status)
    except Exception as e:
        logger.error(f"Brain status error: {e}")
        return jsonify({
            'status': 'error',
            'brain_type': BRAIN_TYPE,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'The requested endpoint does not exist',
        'available_endpoints': [
            '/',
            '/api/chat',
            '/health',
            '/brain/status'
        ],
        'brain_type': BRAIN_TYPE,
        'status': 'error'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'error': 'Internal server error',
        'message': 'Something went wrong on our end',
        'brain_type': BRAIN_TYPE,
        'status': 'error'
    }), 500

if __name__ == '__main__':
    # Get port from environment (Railway sets this)
    port = int(os.environ.get('PORT', 5001))
    
    logger.info(f"Starting Mythiq Assistant with {BRAIN_TYPE} brain on port {port}")
    
    if BRAIN_TYPE == "smart_lightweight":
        logger.info("Brain capabilities: Emotional Intelligence, Context Awareness, Intent Classification")
    else:
        logger.info("Running with simple fallback brain. Upload brain_smart_lightweight.py for full capabilities.")
    
    logger.info("Deployment: Railway-optimized, Professional-grade")
    
    # Run the app
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False  # Set to False for production
    )
