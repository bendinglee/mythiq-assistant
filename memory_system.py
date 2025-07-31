"""
Mythiq Assistant Memory System
Advanced conversation memory and user preference tracking
"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)

@dataclass
class UserPreference:
    """Individual user preference"""
    category: str
    preference: str
    confidence: float
    learned_from: str
    timestamp: str

@dataclass
class ConversationMemory:
    """Memory of a conversation"""
    message: str
    response: str
    intent: str
    emotion: str
    timestamp: str
    topics: List[str]
    user_satisfaction: Optional[float] = None

@dataclass
class UserProfile:
    """Complete user profile with preferences and history"""
    user_id: str
    name: Optional[str] = None
    preferences: List[UserPreference] = None
    conversation_history: List[ConversationMemory] = None
    favorite_topics: List[str] = None
    interaction_count: int = 0
    first_interaction: Optional[str] = None
    last_interaction: Optional[str] = None
    personality_insights: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.preferences is None:
            self.preferences = []
        if self.conversation_history is None:
            self.conversation_history = []
        if self.favorite_topics is None:
            self.favorite_topics = []
        if self.personality_insights is None:
            self.personality_insights = {}

class MythiqMemorySystem:
    """Advanced memory system for personalized interactions"""
    
    def __init__(self, memory_file: str = "mythiq_memory.json"):
        """Initialize memory system"""
        self.memory_file = memory_file
        self.user_profiles: Dict[str, UserProfile] = {}
        self.max_conversation_history = 100  # Per user
        self.max_total_users = 1000
        
        # Learning patterns for preferences
        self.preference_patterns = {
            "game_genres": {
                "keywords": ["platformer", "puzzle", "adventure", "action", "strategy", "rpg"],
                "category": "gaming_preferences"
            },
            "art_styles": {
                "keywords": ["realistic", "cartoon", "abstract", "minimalist", "colorful", "dark"],
                "category": "visual_preferences"
            },
            "interaction_style": {
                "keywords": ["detailed", "quick", "casual", "professional", "creative", "technical"],
                "category": "communication_preferences"
            },
            "project_types": {
                "keywords": ["solo", "collaborative", "learning", "professional", "hobby", "experimental"],
                "category": "project_preferences"
            }
        }
        
        self._load_memory()
        logger.info(f"Memory system initialized with {len(self.user_profiles)} user profiles")

    def _load_memory(self):
        """Load memory from file"""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Convert dictionaries back to UserProfile objects
                for user_id, profile_data in data.get('user_profiles', {}).items():
                    profile = UserProfile(**profile_data)
                    
                    # Convert preference dictionaries to UserPreference objects
                    profile.preferences = [
                        UserPreference(**pref) for pref in profile_data.get('preferences', [])
                    ]
                    
                    # Convert conversation dictionaries to ConversationMemory objects
                    profile.conversation_history = [
                        ConversationMemory(**conv) for conv in profile_data.get('conversation_history', [])
                    ]
                    
                    self.user_profiles[user_id] = profile
                    
        except Exception as e:
            logger.error(f"Error loading memory: {e}")
            self.user_profiles = {}

    def _save_memory(self):
        """Save memory to file"""
        try:
            # Convert UserProfile objects to dictionaries
            data = {
                'user_profiles': {},
                'last_updated': datetime.now().isoformat(),
                'version': '1.0'
            }
            
            for user_id, profile in self.user_profiles.items():
                profile_dict = asdict(profile)
                data['user_profiles'][user_id] = profile_dict
            
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Error saving memory: {e}")

    def get_or_create_user_profile(self, user_id: str) -> UserProfile:
        """Get existing user profile or create new one"""
        if user_id not in self.user_profiles:
            # Clean up if we have too many users
            if len(self.user_profiles) >= self.max_total_users:
                self._cleanup_old_users()
            
            self.user_profiles[user_id] = UserProfile(
                user_id=user_id,
                first_interaction=datetime.now().isoformat()
            )
        
        return self.user_profiles[user_id]

    def remember_conversation(self, user_id: str, message: str, response: str, 
                            intent: str, emotion: str, topics: List[str]):
        """Remember a conversation"""
        profile = self.get_or_create_user_profile(user_id)
        
        # Create conversation memory
        memory = ConversationMemory(
            message=message,
            response=response,
            intent=intent,
            emotion=emotion,
            timestamp=datetime.now().isoformat(),
            topics=topics
        )
        
        # Add to history
        profile.conversation_history.append(memory)
        
        # Limit history size
        if len(profile.conversation_history) > self.max_conversation_history:
            profile.conversation_history = profile.conversation_history[-self.max_conversation_history:]
        
        # Update profile stats
        profile.interaction_count += 1
        profile.last_interaction = memory.timestamp
        
        # Learn preferences from this interaction
        self._learn_preferences(profile, message, intent, topics)
        
        # Update favorite topics
        self._update_favorite_topics(profile, topics)
        
        # Update personality insights
        self._update_personality_insights(profile, emotion, intent)
        
        # Save to file
        self._save_memory()

    def _learn_preferences(self, profile: UserProfile, message: str, intent: str, topics: List[str]):
        """Learn user preferences from conversation"""
        message_lower = message.lower()
        
        for pattern_name, pattern_data in self.preference_patterns.items():
            category = pattern_data["category"]
            
            for keyword in pattern_data["keywords"]:
                if keyword in message_lower:
                    # Check if we already have this preference
                    existing_pref = None
                    for pref in profile.preferences:
                        if pref.category == category and pref.preference == keyword:
                            existing_pref = pref
                            break
                    
                    if existing_pref:
                        # Strengthen existing preference
                        existing_pref.confidence = min(1.0, existing_pref.confidence + 0.1)
                    else:
                        # Add new preference
                        new_pref = UserPreference(
                            category=category,
                            preference=keyword,
                            confidence=0.6,
                            learned_from=intent,
                            timestamp=datetime.now().isoformat()
                        )
                        profile.preferences.append(new_pref)

    def _update_favorite_topics(self, profile: UserProfile, topics: List[str]):
        """Update user's favorite topics"""
        for topic in topics:
            if topic not in profile.favorite_topics:
                profile.favorite_topics.append(topic)
            
            # Keep only top 10 topics
            if len(profile.favorite_topics) > 10:
                # Remove least recent topics (simple approach)
                profile.favorite_topics = profile.favorite_topics[-10:]

    def _update_personality_insights(self, profile: UserProfile, emotion: str, intent: str):
        """Update personality insights based on interactions"""
        insights = profile.personality_insights
        
        # Track emotional patterns
        if "emotions" not in insights:
            insights["emotions"] = {}
        
        if emotion in insights["emotions"]:
            insights["emotions"][emotion] += 1
        else:
            insights["emotions"][emotion] = 1
        
        # Track intent patterns
        if "intents" not in insights:
            insights["intents"] = {}
        
        if intent in insights["intents"]:
            insights["intents"][intent] += 1
        else:
            insights["intents"][intent] = 1
        
        # Derive personality traits
        total_interactions = profile.interaction_count
        if total_interactions >= 5:  # Need some data
            insights["traits"] = self._derive_personality_traits(insights, total_interactions)

    def _derive_personality_traits(self, insights: Dict[str, Any], total_interactions: int) -> List[str]:
        """Derive personality traits from interaction patterns"""
        traits = []
        
        emotions = insights.get("emotions", {})
        intents = insights.get("intents", {})
        
        # Analyze emotional patterns
        excited_ratio = emotions.get("excited", 0) / total_interactions
        curious_ratio = emotions.get("curious", 0) / total_interactions
        creative_ratio = emotions.get("creative", 0) / total_interactions
        
        if excited_ratio > 0.3:
            traits.append("enthusiastic")
        if curious_ratio > 0.2:
            traits.append("inquisitive")
        if creative_ratio > 0.2:
            traits.append("creative")
        
        # Analyze intent patterns
        game_ratio = intents.get("game_request", 0) / total_interactions
        media_ratio = intents.get("media_request", 0) / total_interactions
        help_ratio = intents.get("help_request", 0) / total_interactions
        
        if game_ratio > 0.3:
            traits.append("game_oriented")
        if media_ratio > 0.3:
            traits.append("visually_creative")
        if help_ratio > 0.4:
            traits.append("collaborative")
        
        return traits

    def get_personalized_context(self, user_id: str) -> Dict[str, Any]:
        """Get personalized context for response generation"""
        if user_id not in self.user_profiles:
            return {"is_new_user": True}
        
        profile = self.user_profiles[user_id]
        
        # Get recent conversation topics
        recent_topics = []
        if profile.conversation_history:
            recent_convs = profile.conversation_history[-5:]  # Last 5 conversations
            for conv in recent_convs:
                recent_topics.extend(conv.topics)
        
        # Get top preferences
        top_preferences = {}
        for pref in sorted(profile.preferences, key=lambda x: x.confidence, reverse=True)[:5]:
            if pref.category not in top_preferences:
                top_preferences[pref.category] = []
            top_preferences[pref.category].append(pref.preference)
        
        # Get personality summary
        personality_summary = profile.personality_insights.get("traits", [])
        
        return {
            "is_new_user": False,
            "interaction_count": profile.interaction_count,
            "favorite_topics": profile.favorite_topics[:5],  # Top 5
            "recent_topics": list(set(recent_topics))[:5],  # Unique recent topics
            "preferences": top_preferences,
            "personality_traits": personality_summary,
            "last_emotion": profile.conversation_history[-1].emotion if profile.conversation_history else "neutral",
            "last_intent": profile.conversation_history[-1].intent if profile.conversation_history else "chat"
        }

    def get_conversation_context(self, user_id: str, context_length: int = 3) -> List[Dict[str, str]]:
        """Get recent conversation context"""
        if user_id not in self.user_profiles:
            return []
        
        profile = self.user_profiles[user_id]
        recent_conversations = profile.conversation_history[-context_length:]
        
        return [
            {
                "message": conv.message,
                "response": conv.response,
                "intent": conv.intent,
                "emotion": conv.emotion,
                "timestamp": conv.timestamp
            }
            for conv in recent_conversations
        ]

    def _cleanup_old_users(self):
        """Clean up old inactive users"""
        try:
            # Sort users by last interaction
            sorted_users = sorted(
                self.user_profiles.items(),
                key=lambda x: x[1].last_interaction or x[1].first_interaction or "1970-01-01"
            )
            
            # Keep only the most recent 800 users
            users_to_keep = dict(sorted_users[-800:])
            self.user_profiles = users_to_keep
            
            logger.info(f"Cleaned up old users, now tracking {len(self.user_profiles)} users")
            
        except Exception as e:
            logger.error(f"Error during user cleanup: {e}")

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        total_conversations = sum(len(profile.conversation_history) for profile in self.user_profiles.values())
        total_preferences = sum(len(profile.preferences) for profile in self.user_profiles.values())
        
        # Most common preferences
        all_preferences = {}
        for profile in self.user_profiles.values():
            for pref in profile.preferences:
                key = f"{pref.category}:{pref.preference}"
                all_preferences[key] = all_preferences.get(key, 0) + 1
        
        top_preferences = sorted(all_preferences.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "total_users": len(self.user_profiles),
            "total_conversations": total_conversations,
            "total_preferences": total_preferences,
            "average_conversations_per_user": total_conversations / len(self.user_profiles) if self.user_profiles else 0,
            "top_preferences": top_preferences,
            "memory_file_exists": os.path.exists(self.memory_file)
        }

    def export_user_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Export all data for a specific user"""
        if user_id not in self.user_profiles:
            return None
        
        profile = self.user_profiles[user_id]
        return asdict(profile)

    def delete_user_data(self, user_id: str) -> bool:
        """Delete all data for a specific user"""
        if user_id in self.user_profiles:
            del self.user_profiles[user_id]
            self._save_memory()
            return True
        return False

# Test the memory system
if __name__ == "__main__":
    memory = MythiqMemorySystem("test_memory.json")
    
    # Simulate some interactions
    test_interactions = [
        ("user1", "Hello! I love platformer games", "Hello! Great to meet a platformer fan!", "game_request", "excited", ["games", "platformers"]),
        ("user1", "Can you help me create a colorful puzzle game?", "I'd love to help with your colorful puzzle game!", "game_request", "creative", ["games", "puzzles", "art"]),
        ("user2", "I want to make realistic images", "Realistic images are amazing to create!", "media_request", "confident", ["media", "images"]),
        ("user1", "I'm getting frustrated with the game mechanics", "I understand the frustration with game mechanics", "help_request", "frustrated", ["games", "mechanics"])
    ]
    
    print("🧠 Memory System Test:\n")
    
    for user_id, message, response, intent, emotion, topics in test_interactions:
        memory.remember_conversation(user_id, message, response, intent, emotion, topics)
        print(f"Remembered: {user_id} - {intent} ({emotion})")
    
    print("\n📊 Memory Stats:")
    stats = memory.get_memory_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print("\n👤 User1 Context:")
    context = memory.get_personalized_context("user1")
    for key, value in context.items():
        print(f"{key}: {value}")
    
    # Clean up test file
    if os.path.exists("test_memory.json"):
        os.remove("test_memory.json")

