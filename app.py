"""
Updated app.py for Mythiq Assistant with Smart Lightweight Brain
Railway-optimized Flask server with professional-grade AI
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os
from datetime import datetime

# Import the smart brain
from brain_smart_lightweight import SmartLightweightBrain

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize the smart brain
logger.info("Initializing Smart Lightweight Brain...")
brain = SmartLightweightBrain()
logger.info("Smart Brain initialized successfully!")

@app.route('/')
def home():
    """API information endpoint"""
    return jsonify({
        "message": "Mythiq Assistant API - Smart Lightweight Edition",
        "version": "2.0.0",
        "brain_type": "smart_lightweight_professional",
        "status": "running",
        "endpoints": {
            "chat": "/api/chat (POST)",
            "health": "/health",
            "brain_status": "/brain/status"
        },
        "capabilities": {
            "emotional_intelligence": True,
            "context_awareness": True,
            "intent_classification": True,
            "user_profiling": True,
            "conversation_memory": True,
            "professional_responses": True,
            "railway_optimized": True
        }
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Smart chat endpoint with professional AI"""
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
        
        # Process with smart brain
        response = brain.process_message(message, user_id, session_id)
        
        logger.info(f"Generated response with intent: {response['intent']}, confidence: {response['confidence']:.2f}")
        
        return jsonify({
            'response': response['content'],
            'intent': response['intent'],
            'confidence': response['confidence'],
            'emotion': response['emotion'],
            'context': response['context'],
            'metadata': response['metadata'],
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return jsonify({
            'response': "I'm experiencing a technical moment, but I'm still here and ready to help! Could you try rephrasing that?",
            'intent': 'error',
            'confidence': 0.5,
            'emotion': {'primary': 'neutral', 'intensity': 0.5, 'confidence': 0.5},
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/health')
def health():
    """Health check endpoint for Railway"""
    try:
        health_status = brain.health_check()
        return jsonify(health_status)
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/brain/status')
def brain_status():
    """Detailed brain status and metrics"""
    try:
        status = brain.get_brain_status()
        return jsonify(status)
    except Exception as e:
        logger.error(f"Brain status error: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/conversation/history', methods=['GET'])
def conversation_history():
    """Get conversation history for a user"""
    try:
        user_id = request.args.get('user_id', 'default')
        
        # Get user profile with conversation history
        profile = brain.context_manager.get_or_create_profile(user_id)
        
        return jsonify({
            'user_id': user_id,
            'conversation_count': profile.conversation_count,
            'communication_style': profile.communication_style,
            'preferred_topics': profile.preferred_topics,
            'emotional_patterns': profile.emotional_patterns,
            'last_interaction': profile.last_interaction.isoformat() if profile.last_interaction else None,
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/api/metrics')
def metrics():
    """API usage metrics"""
    try:
        return jsonify({
            'brain_metrics': brain.metrics,
            'active_users': len(brain.context_manager.user_profiles),
            'active_sessions': len(brain.context_manager.active_contexts),
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        })
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        return jsonify({
            'error': str(e),
            'status': 'error'
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
            '/brain/status',
            '/api/conversation/history',
            '/api/metrics'
        ],
        'status': 'error'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'error': 'Internal server error',
        'message': 'Something went wrong on our end',
        'status': 'error'
    }), 500

if __name__ == '__main__':
    # Get port from environment (Railway sets this)
    port = int(os.environ.get('PORT', 5001))
    
    logger.info(f"Starting Mythiq Assistant with Smart Lightweight Brain on port {port}")
    logger.info("Brain capabilities: Emotional Intelligence, Context Awareness, Intent Classification")
    logger.info("Deployment: Railway-optimized, Ultra-lightweight, Professional-grade")
    
    # Run the app
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False  # Set to False for production
    )
