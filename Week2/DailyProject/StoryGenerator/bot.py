import os
from typing import Dict, List
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class StoryGenerator:
    def __init__(self):
        self.api_key = os.getenv('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.client = Groq(api_key=self.api_key)
        
        # Genre options
        self.genres = [
            "Fantasy", "Science Fiction", "Mystery", "Romance", 
            "Horror", "Thriller", "Adventure", "Historical Fiction",
            "Young Adult", "Children's", "Drama", "Comedy",
            "Crime", "Superhero", "Fairy Tale", "Mythology"
        ]
        
        # Length mappings
        self.length_mappings = {
            "Short": "200-300 words",
            "Medium": "400-600 words", 
            "Long": "600-1000 words"
        }
        
        # System prompt for story generation
        self.system_prompt = """You are a creative and imaginative story generator. Your task is to create engaging, well-structured fictional stories based on user prompts.

            Guidelines for story generation:
            1. Create original, creative stories that capture the reader's imagination
            2. Follow the specified genre conventions and tropes
            3. Adhere strictly to the requested word count
            4. Include compelling characters, setting, and plot
            5. Build tension and resolution appropriately
            6. Use vivid descriptions and sensory details
            7. Maintain consistent tone and style throughout
            8. Provide a satisfying ending that ties the story together

            Story Structure:
            - Beginning: Introduce characters, setting, and initial situation
            - Middle: Develop conflict, build tension, and advance plot
            - End: Resolve the main conflict and provide closure

            Always ensure the story is appropriate and engaging for general audiences."""

    def generate_story(self, story_idea: str, genre: str, length: str) -> Dict[str, str]:
        """Generate a story based on user input"""
        if not story_idea.strip():
            return {"error": "Please provide a story idea or description"}
        
        # Prepare the user prompt
        word_range = self.length_mappings.get(length, "500-800 words")
        
        user_prompt = f"""
            Please generate a {genre.lower()} story based on the following idea:

            **Story Idea**: {story_idea}
            **Genre**: {genre}
            **Length**: {word_range}

            Requirements:
            - Create a complete, self-contained story
            - Use appropriate elements and tropes from the {genre} genre
            - Ensure the story is between {word_range}
            - Include engaging characters and a clear plot structure
            - Provide a satisfying conclusion

            Please write the story now:
            """

        try:
            # Call Groq API
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.8,  # Higher temperature for creativity
                max_tokens=2048,   # Allow longer responses for stories
                top_p=0.9,
                stream=False
            )

            story_content = response.choices[0].message.content
            
            return {
                "story": story_content,
                "genre": genre,
                "length": length,
                "word_range": word_range,
                "success": True
            }

        except Exception as e:
            return {"error": f"Sorry, I encountered an error generating your story: {str(e)}"}

    def get_genres(self) -> List[str]:
        """Get available genres"""
        return self.genres

    def get_length_options(self) -> List[str]:
        """Get available length options"""
        return list(self.length_mappings.keys())

    def analyze_story_idea(self, story_idea: str) -> str:
        """Provide feedback on a story idea"""
        if not story_idea.strip():
            return "Please provide a story idea to analyze."
        
        analysis_prompt = f"""
        Analyze this story idea and provide constructive feedback:
        
        Story Idea: "{story_idea}"
        
        Please provide:
        1. Strengths of the idea
        2. Potential challenges
        3. Genre suggestions
        4. Plot development ideas
        5. Character suggestions
        
        Keep the analysis brief and helpful.
        """

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a creative writing coach providing constructive feedback on story ideas."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.7,
                max_tokens=512,
                top_p=1,
                stream=False
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"Unable to analyze the story idea: {str(e)}"