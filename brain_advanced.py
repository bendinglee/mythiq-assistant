"""
Mythiq Assistant Brain - Advanced Free AI System
Professional-grade conversation engine with emotional intelligence
"""
import json
import re
import random
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import logging

# Free NLP libraries
from textblob import TextBlob
try:
    from fuzzywuzzy import fuzz
except ImportError:
    # Fallback if fuzzywuzzy not available
    def fuzz_ratio(a, b):
        return 50  # Default similarity

logger = logging.getLogger(__name__)

@dataclass
class ConversationContext:
    """Tracks conversation context and flow"""
    user_id: str
    session_id: str
    current_topic: str = "general"
    mood: str = "neutral"
    last_intent: str = "chat"
    conversation_length: int = 0
    topics_discussed: List[str] = None
    user_preferences: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.topics_discussed is None:
            self.topics_discussed = []
        if self.user_preferences is None:
            self.user_preferences = {}

@dataclass
class AIResponse:
    """Structured AI response with metadata"""
    content: str
    intent: str
    confidence: float
    emotion: str
    context_used: bool = False
    personality_traits: List[str] = None
    suggested_actions: List[str] = None
    
    def __post_init__(self):
        if self.personality_traits is None:
            self.personality_traits = []
        if self.suggested_actions is None:
            self.suggested_actions = []

class AdvancedMythiqBrain:
    """Advanced AI brain with emotional intelligence and memory"""
    
    def __init__(self):
        """Initialize the advanced brain system"""
        logger.info("Initializing Advanced Mythiq Brain...")
        
        # Core personality traits
        self.personality = {
            "name": "Mythiq",
            "traits": ["helpful", "creative", "encouraging", "knowledgeable", "empathetic"],
            "communication_style": "friendly_professional",
            "expertise": ["games", "media", "creativity", "problem_solving"],
            "values": ["creativity", "learning", "collaboration", "growth"]
        }
        
        # Emotional intelligence patterns
        self.emotion_patterns = {
            "excited": ["amazing", "awesome", "great", "love", "fantastic", "wonderful"],
            "frustrated": ["stuck", "hard", "difficult", "can't", "impossible", "hate"],
            "curious": ["how", "what", "why", "when", "where", "explain"],
            "confident": ["will", "can", "definitely", "sure", "absolutely"],
            "uncertain": ["maybe", "perhaps", "not sure", "don't know", "confused"],
            "creative": ["idea", "create", "make", "build", "design", "imagine"]
        }
        
        # Intent recognition patterns
        self.intent_patterns = {
            "game_request": {
                "keywords": ["game", "play", "level", "character", "adventure", "puzzle", "platformer"],
                "phrases": ["create a game", "make a game", "game idea", "game development"],
                "confidence_boost": 0.2
            },
            "media_request": {
                "keywords": ["image", "video", "picture", "create", "generate", "media", "visual"],
                "phrases": ["create an image", "make a video", "generate media"],
                "confidence_boost": 0.2
            },
            "help_request": {
                "keywords": ["help", "assist", "support", "guide", "explain", "how"],
                "phrases": ["can you help", "need help", "how do i", "please help"],
                "confidence_boost": 0.1
            },
            "creative_brainstorm": {
                "keywords": ["idea", "brainstorm", "creative", "inspiration", "concept"],
                "phrases": ["need ideas", "brainstorm with me", "creative help"],
                "confidence_boost": 0.15
            }
        }
        
        # Response templates with personality
        self.response_templates = {
            "greeting": {
                "excited": [
                    "Hello there! I'm Mythiq, and I'm absolutely thrilled to meet you! 🌟 I'm here to help you bring your wildest creative ideas to life. What amazing project shall we work on together?",
                    "Hey! Welcome to the creative zone! I'm Mythiq, your AI companion for all things games, media, and imagination. I can already sense the creative energy - what's brewing in that brilliant mind of yours?",
                    "Greetings, creative soul! I'm Mythiq, and I live for moments like this - when someone new joins our creative community! Whether it's games, media, or just brainstorming, I'm here to make magic happen with you!"
                ],
                "neutral": [
                    "Hello! I'm Mythiq, your creative AI assistant. I specialize in helping with games, media creation, and bringing ideas to life. How can I help you create something amazing today?",
                    "Hi there! I'm Mythiq, and I'm here to help you with creative projects, problem-solving, and turning ideas into reality. What would you like to work on?",
                    "Welcome! I'm Mythiq, your AI companion for creativity and innovation. Whether you're thinking games, media, or just need to brainstorm, I'm ready to dive in!"
                ]
            },
            "game_request": {
                "excited": [
                    "YES! Game development is one of my absolute favorite topics! 🎮 I can already feel the creative energy flowing. Tell me, what kind of gaming experience do you want to create? Are we talking epic adventures, mind-bending puzzles, or maybe something completely unique?",
                    "Oh, this is fantastic! Creating games is like digital alchemy - turning ideas into interactive experiences! I'm buzzing with excitement to help you craft something special. What genre speaks to your creative soul?",
                    "Game creation time! This is where magic happens! 🌟 I love how games can transport people to entirely new worlds. What's your vision? Are you dreaming of platformers, RPGs, puzzles, or perhaps something that's never been done before?"
                ],
                "encouraging": [
                    "I love that you want to create a game! Game development is such a rewarding creative journey, and I'm here to support you every step of the way. What type of game experience are you hoping to build?",
                    "That's wonderful! Games are incredible mediums for storytelling and creativity. Whether you're a beginner or experienced, we can definitely make something amazing together. What's your game concept?",
                    "Perfect! Game creation is one of the most fulfilling creative pursuits. I'm excited to help you turn your vision into reality. What kind of gameplay experience do you have in mind?"
                ]
            },
            "media_request": {
                "creative": [
                    "Ooh, media creation! This is where artistry meets technology, and I absolutely love it! 🎨 Whether we're talking images, videos, or something entirely new, I'm here to help you craft something visually stunning. What's your creative vision?",
                    "Media creation is pure magic! There's something incredible about bringing visual ideas to life. I'm excited to help you explore the possibilities - are you thinking images, videos, animations, or maybe a combination?",
                    "Yes! Visual storytelling is one of humanity's most powerful forms of expression! I'm thrilled to help you create something that will captivate and inspire. What kind of media are you envisioning?"
                ],
                "supportive": [
                    "I'd be delighted to help you with media creation! Visual content is such a powerful way to express ideas and connect with people. What type of media project are you working on?",
                    "Media creation is a fantastic way to bring ideas to life! I'm here to help you through the creative process, whether it's planning, conceptualizing, or execution. What's your project about?",
                    "That sounds like an exciting creative project! I love helping people turn their visual ideas into reality. Tell me more about what you'd like to create!"
                ]
            },
            "frustrated_user": [
                "I can sense some frustration in your message, and I want you to know that's completely normal and okay! 💙 Creative challenges are part of the journey, and they often lead to the most breakthrough moments. Let's tackle this together - what's feeling most overwhelming right now?",
                "Hey, I hear you. Sometimes creative projects can feel like climbing a mountain, but remember - every expert was once a beginner, and every masterpiece started with someone feeling exactly like you do right now. What specific part is giving you trouble?",
                "I can feel the challenge you're facing, and I want you to know you're not alone in this! Some of the most amazing creations come from pushing through these tough moments. Let's break this down into smaller, manageable pieces. What's the biggest obstacle right now?"
            ],
            "encouraging_progress": [
                "I love seeing your creative journey unfold! 🌱 Every step you're taking is building toward something amazing. Your dedication and curiosity are exactly what make great creators. What's the next piece of the puzzle we should tackle?",
                "You're doing fantastic work! I can see how your ideas are evolving and growing stronger with each interaction. This is exactly how innovation happens - one thoughtful step at a time. What aspect excites you most right now?",
                "This is wonderful progress! I'm genuinely impressed by how you're approaching this challenge. Your creative process is inspiring to watch unfold. What direction feels most promising to explore next?"
            ]
        }
        
        # Context tracking
        self.active_contexts: Dict[str, ConversationContext] = {}
        
        logger.info("Advanced Mythiq Brain initialized successfully!")

    def process_message(self, message: str, user_id: str = "default", session_id: str = None) -> AIResponse:
        """Process a message with advanced AI capabilities"""
        try:
            # Initialize or get context
            context_key = f"{user_id}_{session_id or 'default'}"
            if context_key not in self.active_contexts:
                self.active_contexts[context_key] = ConversationContext(
                    user_id=user_id,
                    session_id=session_id or "default"
                )
            
            context = self.active_contexts[context_key]
            context.conversation_length += 1
            
            # Analyze message
            emotion = self._analyze_emotion(message)
            intent, confidence = self._detect_intent(message, context)
            
            # Update context
            context.mood = emotion
            context.last_intent = intent
            if intent not in context.topics_discussed:
                context.topics_discussed.append(intent)
            
            # Generate response
            response_content = self._generate_contextual_response(
                message, intent, emotion, context, confidence
            )
            
            # Create structured response
            response = AIResponse(
                content=response_content,
                intent=intent,
                confidence=confidence,
                emotion=emotion,
                context_used=context.conversation_length > 1,
                personality_traits=self._get_active_traits(intent, emotion),
                suggested_actions=self._get_suggested_actions(intent)
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return AIResponse(
                content="I'm having a moment of technical difficulty, but I'm still here and ready to help! Could you try rephrasing that?",
                intent="error",
                confidence=0.5,
                emotion="neutral"
            )

    def _analyze_emotion(self, message: str) -> str:
        """Analyze emotional content of message"""
        try:
            # Use TextBlob for basic sentiment
            blob = TextBlob(message)
            polarity = blob.sentiment.polarity
            
            # Enhanced emotion detection with patterns
            message_lower = message.lower()
            emotion_scores = {}
            
            for emotion, patterns in self.emotion_patterns.items():
                score = sum(1 for pattern in patterns if pattern in message_lower)
                if score > 0:
                    emotion_scores[emotion] = score
            
            # Combine sentiment with pattern matching
            if emotion_scores:
                primary_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0]
                
                # Adjust based on sentiment polarity
                if polarity > 0.3 and primary_emotion not in ["excited", "confident"]:
                    return "excited"
                elif polarity < -0.3 and primary_emotion not in ["frustrated"]:
                    return "frustrated"
                else:
                    return primary_emotion
            
            # Fallback to sentiment-based emotion
            if polarity > 0.1:
                return "excited"
            elif polarity < -0.1:
                return "frustrated"
            else:
                return "neutral"
                
        except Exception as e:
            logger.error(f"Error in emotion analysis: {e}")
            return "neutral"

    def _detect_intent(self, message: str, context: ConversationContext) -> Tuple[str, float]:
        """Detect user intent with confidence scoring"""
        message_lower = message.lower()
        intent_scores = {}
        
        # Score each intent
        for intent, patterns in self.intent_patterns.items():
            score = 0
            
            # Keyword matching
            keyword_matches = sum(1 for keyword in patterns["keywords"] if keyword in message_lower)
            score += keyword_matches * 0.3
            
            # Phrase matching
            phrase_matches = sum(1 for phrase in patterns["phrases"] if phrase in message_lower)
            score += phrase_matches * 0.5
            
            # Context boost
            if intent == context.last_intent:
                score += 0.1
            
            # Confidence boost
            score += patterns.get("confidence_boost", 0)
            
            if score > 0:
                intent_scores[intent] = score
        
        # Determine best intent
        if intent_scores:
            best_intent = max(intent_scores.items(), key=lambda x: x[1])
            return best_intent[0], min(best_intent[1], 1.0)
        
        # Default to chat
        return "chat", 0.6

    def _generate_contextual_response(self, message: str, intent: str, emotion: str, 
                                    context: ConversationContext, confidence: float) -> str:
        """Generate contextually appropriate response"""
        
        # Handle greetings
        if any(word in message.lower() for word in ["hello", "hi", "hey", "greetings"]):
            templates = self.response_templates["greeting"][emotion if emotion in ["excited", "neutral"] else "neutral"]
            return random.choice(templates)
        
        # Handle frustrated users with empathy
        if emotion == "frustrated":
            return random.choice(self.response_templates["frustrated_user"])
        
        # Handle specific intents
        if intent in ["game_request", "media_request"]:
            emotion_key = emotion if emotion in ["excited", "encouraging", "creative", "supportive"] else "encouraging"
            if intent == "game_request":
                templates = self.response_templates["game_request"].get(emotion_key, 
                    self.response_templates["game_request"]["encouraging"])
            else:
                templates = self.response_templates["media_request"].get(emotion_key,
                    self.response_templates["media_request"]["supportive"])
            
            response = random.choice(templates)
            
            # Add context if available
            if context.conversation_length > 3:
                response += f"\n\nI've noticed we've been exploring {', '.join(context.topics_discussed[-2:])} together - I love seeing how your ideas are developing!"
            
            return response
        
        # Encouraging responses for ongoing conversations
        if context.conversation_length > 2 and emotion in ["excited", "confident", "creative"]:
            return random.choice(self.response_templates["encouraging_progress"])
        
        # Default intelligent response
        return self._generate_intelligent_default(message, context, emotion)

    def _generate_intelligent_default(self, message: str, context: ConversationContext, emotion: str) -> str:
        """Generate intelligent default responses"""
        
        # Analyze message content for smart responses
        message_lower = message.lower()
        
        # Question responses
        if any(word in message_lower for word in ["what", "how", "why", "when", "where"]):
            return f"That's a great question! I love how curious you are. {self._get_contextual_help(message, context)} What specific aspect would you like to explore deeper?"
        
        # Sharing/telling responses  
        if any(word in message_lower for word in ["i think", "i believe", "i want", "i need"]):
            return f"I appreciate you sharing that with me! {self._get_encouraging_response(emotion)} Tell me more about what's driving this idea."
        
        # Problem-solving responses
        if any(word in message_lower for word in ["problem", "issue", "trouble", "stuck"]):
            return "I hear you're facing a challenge, and I'm here to help you work through it! Let's break this down step by step. What's the core issue you're dealing with?"
        
        # Default with personality
        responses = [
            f"That's really interesting! I can sense your {emotion} energy about this. What aspect excites you most?",
            f"I love how you're thinking about this! Your {emotion} approach is exactly what creative projects need. What's the next step you're considering?",
            f"This conversation is fascinating! I'm getting a {emotion} vibe from you, which tells me you're really engaged with this topic. What direction should we explore?"
        ]
        
        return random.choice(responses)

    def _get_contextual_help(self, message: str, context: ConversationContext) -> str:
        """Provide contextual help based on conversation history"""
        if "game" in context.topics_discussed:
            return "Based on our game discussions, I think I can provide some targeted insights."
        elif "media" in context.topics_discussed:
            return "Given our media creation conversations, I have some specific ideas that might help."
        else:
            return "I'm here to help with whatever creative challenge you're facing."

    def _get_encouraging_response(self, emotion: str) -> str:
        """Get encouraging response based on emotion"""
        encouragements = {
            "excited": "Your enthusiasm is contagious!",
            "frustrated": "I can feel your determination, and that's exactly what leads to breakthroughs!",
            "curious": "Your curiosity is one of your greatest creative assets!",
            "confident": "I love your confidence - that's the mindset that creates amazing things!",
            "creative": "Your creative thinking is inspiring!"
        }
        return encouragements.get(emotion, "Your thoughtful approach is really impressive!")

    def _get_active_traits(self, intent: str, emotion: str) -> List[str]:
        """Get personality traits active in this response"""
        base_traits = ["helpful", "encouraging"]
        
        if intent in ["game_request", "media_request"]:
            base_traits.append("creative")
        
        if emotion == "frustrated":
            base_traits.extend(["empathetic", "supportive"])
        elif emotion == "excited":
            base_traits.extend(["enthusiastic", "inspiring"])
        
        return base_traits

    def _get_suggested_actions(self, intent: str) -> List[str]:
        """Get suggested follow-up actions"""
        actions = {
            "game_request": ["explore_genres", "define_mechanics", "create_prototype"],
            "media_request": ["define_style", "gather_references", "plan_creation"],
            "help_request": ["break_down_problem", "identify_resources", "create_action_plan"],
            "creative_brainstorm": ["expand_ideas", "explore_variations", "combine_concepts"]
        }
        return actions.get(intent, ["continue_conversation", "ask_questions", "explore_ideas"])

    def get_personality_info(self) -> Dict[str, Any]:
        """Get current personality configuration"""
        return {
            "personality": self.personality,
            "active_contexts": len(self.active_contexts),
            "capabilities": [
                "emotional_intelligence",
                "context_awareness", 
                "creative_brainstorming",
                "intent_recognition",
                "personality_consistency"
            ]
        }

    def health_check(self) -> Dict[str, Any]:
        """Advanced health check with detailed status"""
        return {
            "status": "healthy",
            "brain_type": "advanced_free_ai",
            "capabilities": {
                "emotional_intelligence": True,
                "context_awareness": True,
                "intent_recognition": True,
                "personality_system": True,
                "memory_system": True,
                "creative_assistance": True
            },
            "active_sessions": len(self.active_contexts),
            "personality": self.personality["name"],
            "response_quality": "professional_grade",
            "cost": "free",
            "reliability": "high"
        }

# Test the advanced brain
if __name__ == "__main__":
    brain = AdvancedMythiqBrain()
    
    test_messages = [
        ("Hello there!", "user1", "session1"),
        ("I want to create an amazing platformer game!", "user1", "session1"),
        ("This is so hard, I'm getting frustrated", "user1", "session1"),
        ("Actually, I'm getting excited about this project!", "user1", "session1"),
        ("Can you help me with some creative ideas?", "user2", "session2")
    ]
    
    print("🧠 Advanced Mythiq Brain Test Results:\n")
    
    for message, user_id, session_id in test_messages:
        print(f"User: {message}")
        response = brain.process_message(message, user_id, session_id)
        print(f"Mythiq: {response.content}")
        print(f"Intent: {response.intent} | Emotion: {response.emotion} | Confidence: {response.confidence:.2f}")
        print(f"Traits: {', '.join(response.personality_traits)}")
        print("-" * 80)
    
    print("\n🔍 Brain Health Check:")
    health = brain.health_check()
    for key, value in health.items():
        print(f"{key}: {value}")

