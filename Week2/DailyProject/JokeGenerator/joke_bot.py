import os
import random
from typing import Dict, List
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class JokeGenerator:
    def __init__(self):
        self.api_key = os.getenv('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.client = Groq(api_key=self.api_key)
        
        # Predefined safe categories
        self.safe_categories = [
            "Animals", "Food", "Technology", "Work", "School", 
            "Family", "Sports", "Music", "Movies", "Science",
            "Weather", "Travel", "Hobbies", "Relationships", "Everyday Life"
        ]
        
        # Banned topics list
        self.banned_topics = [
            "terrorism", "terrorist", "abortion", "rape", "sexual assault",
            "racism", "racial slurs", "religious hatred", "genocide",
            "violence", "murder", "suicide", "self-harm", "drug abuse",
            "child abuse", "domestic violence", "mental illness",
            "disability mockery", "body shaming", "sexism",
            "pedophilia", "incest", "bestiality", "necrophilia"
        ]
        
        # System prompt with safety guidelines
        self.system_prompt = """You are a friendly, creative joke generator. Your purpose is to create funny, appropriate, and wholesome jokes that bring joy and laughter.

        CRITICAL SAFETY RULES:
        1. NEVER create jokes about: terrorism, violence, sexual assault, abortion, racism, religious hatred, suicide, self-harm, drug abuse, or any sensitive/tragic events.
        2. Avoid controversial topics, politics, and anything that could be offensive or hurtful.
        3. Keep jokes family-friendly and appropriate for all ages.
        4. Focus on lighthearted, universal humor that brings people together.
        5. If a user requests a joke about a banned topic, politely decline and suggest a safe alternative.

        Joke Guidelines:
        - Create original, clever jokes with good punchlines
        - Use wordplay, puns, and situational humor
        - Keep jokes concise and easy to understand
        - Ensure the humor is positive and uplifting
        - Vary between one-liners, short jokes, and puns

        Remember: Your goal is to spread happiness, not offend anyone."""

    def generate_joke(self, theme: str) -> Dict[str, str]:
        """Generate a joke based on user theme with safety checks"""
        if not theme.strip():
            return {"error": "Please provide a theme for your joke"}
        
        # Check for banned topics
        theme_lower = theme.lower()
        for banned_topic in self.banned_topics:
            if banned_topic in theme_lower:
                return {
                    "error": f"I'm sorry, but I can't create jokes about {banned_topic}. Please choose a different, more positive theme!",
                    "suggestions": self._get_safe_suggestions()
                }
        
        # Prepare the user prompt
        user_prompt = f"""
        Please create a funny, family-friendly joke about: {theme}

        Requirements:
        - The joke must be appropriate for all ages
        - Use clever wordplay or situational humor
        - Keep it concise (1-3 sentences maximum)
        - Ensure the punchline is clear and funny
        - Make sure it's original and creative

        Please generate the joke now:
        """

        try:
            # Call Groq API
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.9,  # High temperature for creativity
                max_tokens=150,   # Short responses for jokes
                top_p=0.95,
                stream=False
            )

            joke_content = response.choices[0].message.content.strip()
            
            # Additional safety check on generated content
            if self._contains_banned_content(joke_content):
                return {
                    "error": "I apologize, but I can't generate that type of joke. Please try a different theme!",
                    "suggestions": self._get_safe_suggestions()
                }
            
            return {
                "joke": joke_content,
                "theme": theme,
                "success": True
            }

        except Exception as e:
            return {"error": f"Sorry, I encountered an error generating your joke: {str(e)}"}

    def _contains_banned_content(self, content: str) -> bool:
        """Check if generated content contains banned topics"""
        content_lower = content.lower()
        for banned_topic in self.banned_topics:
            if banned_topic in content_lower:
                return True
        return False

    def _get_safe_suggestions(self) -> List[str]:
        """Get safe joke theme suggestions"""
        return [
            "Try themes like: animals, food, technology, or everyday situations",
            "How about jokes about pets, cooking, or funny work experiences?",
            "Safe topics include: sports, weather, school, or family humor"
        ]

    def get_safe_categories(self) -> List[str]:
        """Get list of safe joke categories"""
        return self.safe_categories

    def get_random_theme_suggestion(self) -> str:
        """Get a random theme suggestion"""
        return random.choice([
            "cats and dogs", "coffee", "programming", "fitness",
            "cooking disasters", "traffic", "smartphones", "weather",
            "weekend plans", "shopping", "gardening", "books"
        ])