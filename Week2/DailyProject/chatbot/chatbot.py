import os
import json
from typing import List, Dict, Optional, Tuple
from groq import Groq
from ddgs import DDGS
import requests
from dotenv import load_dotenv

load_dotenv()

class GroqChatBot:
    def __init__(self):
        self.api_key = os.getenv('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.client = Groq(api_key=self.api_key)
        self.conversation_history: List[Dict] = []
        self.search_enabled = False
        self.max_history_length = 12  # 6 exchanges
        self.last_search_results: List[Dict] = []
        
        # System prompt for the chatbot
        self.system_prompt = """You are an AI assistant with access to real-time internet search capabilities. Your role is to provide helpful, accurate, and concise responses.

        Guidelines:
        1. Be conversational and friendly
        2. Use the conversation history for context
        3. When search is enabled, use the search results to provide current information
        4. When search is disabled, rely on your knowledge and be honest about limitations
        5. Keep responses focused and informative
        6. If search results are available, cite key information but don't list all results
        7. Always maintain a helpful and professional tone

        Important: When search results are provided, use them to enhance your response. If the search results don't contain relevant information, acknowledge this and provide the best response you can based on your knowledge."""

    def toggle_search(self, enabled: bool) -> str:
        """Toggle internet search on/off"""
        self.search_enabled = enabled
        status = "enabled" if enabled else "disabled"
        return f"🔍 Internet search has been {status}"

    def search_web(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search the web using DuckDuckGo and return results with URLs and snippets"""
        try:
            with DDGS() as ddgs:
                results = []
                search_iter = ddgs.text(query, max_results=max_results)
                for r in search_iter:
                    title = r.get("title", "No title")
                    url = r.get("href", "")
                    snippet = r.get("body", "No description available")
                    
                    results.append({
                        "title": title,
                        "url": url,
                        "snippet": snippet
                    })
                return results
        except Exception as e:
            print(f"Search error: {e}")
            return []

    def format_search_results(self, search_results: List[Dict]) -> str:
        """Format search results for the prompt"""
        if not search_results:
            return "No search results found for the query."

        formatted = "Current search results:\n\n"
        for i, result in enumerate(search_results[:3], 1):
            title = result.get('title', 'No title')
            snippet = result.get('snippet', 'No description available')
            formatted += f"RESULT {i}:\n"
            formatted += f"Title: {title}\n"
            formatted += f"Content: {snippet}\n\n"
        
        return formatted

    def generate_response(self, user_input: str) -> Tuple[str, List[Dict]]:
        """Generate response using Groq and Llama3, return response and search sources"""
        if not user_input.strip():
            return "Please enter a message.", []

        # Clear previous search results
        self.last_search_results = []

        # Add user message to conversation history
        self.conversation_history.append({"role": "user", "content": user_input})

        # Prepare messages for the API
        messages = [{"role": "system", "content": self.system_prompt}]

        # Add conversation history (last 5 exchanges)
        for msg in self.conversation_history[-self.max_history_length:]:
            messages.append(msg)

        # Perform web search if enabled and add results to context
        search_context = ""
        if self.search_enabled:
            search_results = self.search_web(user_input)
            self.last_search_results = search_results  # Store for displaying sources
            
            if search_results:
                search_context = self.format_search_results(search_results)
                # Add search context as a system message
                messages.append({
                    "role": "system", 
                    "content": f"Current web search results:\n{search_context}\n\nUse these search results to provide accurate and current information. Cite the most relevant findings."
                })

        try:
            # Call Groq API
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",  # Using Llama3 8B model
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
                top_p=1,
                stream=False
            )

            bot_response = response.choices[0].message.content

            # Add bot response to conversation history
            self.conversation_history.append({"role": "assistant", "content": bot_response})

            return bot_response, self.last_search_results

        except Exception as e:
            error_msg = f"Sorry, I encountered an error: {str(e)}"
            self.conversation_history.append({"role": "assistant", "content": error_msg})
            return error_msg, []

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        self.last_search_results = []
        return "Conversation history cleared."

    def get_conversation_history(self) -> List[Dict]:
        """Get the conversation history"""
        return self.conversation_history.copy()

    def export_history(self) -> str:
        """Export conversation history as JSON string"""
        return json.dumps(self.conversation_history, indent=2)

    def get_last_search_results(self) -> List[Dict]:
        """Get the last search results"""
        return self.last_search_results.copy()