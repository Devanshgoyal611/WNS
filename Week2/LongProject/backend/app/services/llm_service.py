import groq
import google.generativeai as genai
from ..config import settings
from typing import Optional, List
import time

class LLMService:
    def __init__(self):
        self.groq_client = groq.Client(api_key=settings.GROQ_API_KEY)
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        
    async def generate_response_groq(self, prompt: str, model: str, conversation_history: List) -> str:
        try:
            # Format conversation history
            messages = []
            for msg in conversation_history[-10:]:  # Last 10 messages
                if isinstance(msg, dict):
                    text = msg.get("message", "")
                    is_user = msg.get("is_user", "assistant")
                else:
                    # object-like (Pydantic model or custom)
                    # use getattr fallback to support both styles
                    is_user = getattr(msg, "is_user", "assistant")
                    text = getattr(msg, "message", None)
                    
                role = is_user
                messages.append({"role": role, "content": text})
            
            messages.append({"role": "user", "content": prompt})
            
            response = self.groq_client.chat.completions.create(
                model=settings.GROQ_MODELS[model],
                messages=messages,
                temperature=0.1,
                max_tokens=1024
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    async def generate_response_gemini(self, prompt: str, conversation_history: List) -> str:
        try:
            model = genai.GenerativeModel('gemma-3-27b-it')
            
            # Format history
            history = []
            for msg in conversation_history[-10:]:
                if isinstance(msg, dict):
                    text = msg.get("message", "")
                    is_user = msg.get("is_user", "assistant")
                else:
                    # object-like (Pydantic model or custom)
                    # use getattr fallback to support both styles
                    is_user = getattr(msg, "is_user", "assistant")
                    text = getattr(msg, "message", None)
                    
                role = is_user
                history.append({"role": role, "content": text})
            
            context = "\n".join(history)
            full_prompt = f"Context:\n{context}\n\nCurrent Question: {prompt}"
            
            response = model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            return f"Error generating response: {str(e)}"

llm_service = LLMService()