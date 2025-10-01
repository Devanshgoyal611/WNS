import streamlit as st
import json
from typing import List, Dict
from chatbot import GroqChatBot
import os
from dotenv import load_dotenv

load_dotenv()

class StreamlitChatApp:
    def __init__(self):
        self.chatbot = None
        self.initialize_chatbot()

    def initialize_chatbot(self):
        """Initialize the chatbot instance"""
        try:
            if 'chatbot' not in st.session_state:
                st.session_state.chatbot = GroqChatBot()
            self.chatbot = st.session_state.chatbot
        except Exception as e:
            st.error(f"Failed to initialize chatbot: {e}")

    def setup_page(self):
        """Configure Streamlit page settings"""
        st.set_page_config(
            page_title="AI ChatBot with Groq & Web Search",
            page_icon="🤖",
            layout="wide",
            initial_sidebar_state="expanded"
        )

        # Custom CSS
        st.markdown("""
        <style>
        .chat-message {
            padding: 1.5rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
            display: flex;
            flex-direction: column;
        }
        .chat-message.user {
            background-color: #2b313e;
            border-left: 5px solid #ff4b4b;
        }
        .chat-message.assistant {
            background-color: #1a1d29;
            border-left: 5px solid #00d4aa;
        }
        .chat-message .avatar {
            width: 20%;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        .source-link {
            background-color: #2b313e;
            padding: 0.5rem;
            border-radius: 0.25rem;
            margin: 0.25rem 0;
            border-left: 3px solid #ffd700;
        }
        </style>
        """, unsafe_allow_html=True)

    def render_sidebar(self):
        """Render the sidebar with controls"""
        with st.sidebar:
            st.title("🤖 ChatBot Controls")
            st.markdown("---")
            
            # API Key info
            if os.getenv('GROQ_API_KEY'):
                st.success("✅ GROQ API Key Loaded")
            else:
                st.error("❌ GROQ API Key Missing")
                st.info("Add GROQ_API_KEY to your .env file")
            
            # Search toggle
            if self.chatbot:
                search_status = st.toggle(
                    "🔍 Enable Web Search",
                    value=self.chatbot.search_enabled,
                    help="Toggle internet search using DuckDuckGo"
                )
                if search_status != self.chatbot.search_enabled:
                    status_msg = self.chatbot.toggle_search(search_status)
                    st.success(status_msg)
                    st.rerun()
            
            # Display current search status
            if self.chatbot:
                status_color = "🟢" if self.chatbot.search_enabled else "🔴"
                st.markdown(f"### Search Status: {status_color}")
                if self.chatbot.search_enabled:
                    st.success("Web search is **ENABLED** - I can access current information")
                else:
                    st.warning("Web search is **DISABLED** - Using knowledge base only")
            
            st.markdown("---")
            
            # Model info
            st.subheader("🔧 Technical Info")
            st.markdown("""
            **Model:** Llama3.3 70B
            **Provider:** Groq
            **Search:** DuckDuckGo
            **Memory:** Session-based
            """)
            
            st.markdown("---")
            
            # Conversation controls
            st.subheader("💬 Conversation")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Clear History", use_container_width=True):
                    if self.chatbot:
                        self.chatbot.clear_history()
                        st.session_state.messages = []
                        st.session_state.sources = []
                        st.success("History cleared!")
                        st.rerun()
            
            with col2:
                if st.button("🔄 Refresh", use_container_width=True):
                    st.rerun()
            
            # Export chat
            if self.chatbot and self.chatbot.get_conversation_history():
                history_json = self.chatbot.export_history()
                st.download_button(
                    label="💾 Export Chat as JSON",
                    data=history_json,
                    file_name="chat_history.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            st.markdown("---")
            
            # Features info
            st.subheader("🚀 Features")
            st.markdown("""
            - **💬 Smart Conversations** with Groq & Llama3
            - **🔍 Real-time Web Search** with DuckDuckGo
            - **🧠 Conversation Memory**
            - **📝 Export Conversations**
            - **⚡ Fast Responses**
            - **🔗 Source Citations**
            """)

    def render_sources(self, sources: List[Dict]):
        """Render search sources with URLs"""
        if sources:
            with st.expander("🔍 **Sources from Web Search**", expanded=True):
                for i, source in enumerate(sources[:3], 1):
                    title = source.get('title', 'No title')
                    url = source.get('url', '')
                    snippet = source.get('snippet', 'No description available')
                    
                    st.markdown(f"**{i}. {title}**")
                    if url:
                        st.markdown(f"🔗 [Source Link]({url})")
                    st.markdown(f"*{snippet[:150]}...*")
                    st.markdown("---")

    def render_chat_interface(self):
        """Render the main chat interface"""
        st.title("🤖 AI ChatBot with Groq & Web Search")
        
        # Status indicators
        col1, col2, col3 = st.columns(3)
        with col1:
            if self.chatbot:
                status = "🟢 Enabled" if self.chatbot.search_enabled else "🔴 Disabled"
                st.metric("Web Search", status)
        
        with col2:
            if self.chatbot:
                history_count = len(self.chatbot.get_conversation_history()) // 2
                st.metric("Messages", history_count)
        
        with col3:
            st.metric("Model", "Llama3.3 70B")
        
        st.markdown("---")
        
        # Initialize chat history and sources
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        if "sources" not in st.session_state:
            st.session_state.sources = []
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
                # Show sources for assistant messages if available
                if message["role"] == "assistant" and message.get("sources"):
                    self.render_sources(message["sources"])
        
        # Chat input
        if prompt := st.chat_input("Type your message here..."):
            if not self.chatbot:
                st.error("ChatBot not initialized. Please check your API key.")
                return
            
            # Add user message to chat
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate and display bot response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..." + (" 🔍 Searching web..." if self.chatbot.search_enabled else "")):
                    response, sources = self.chatbot.generate_response(prompt)
                    st.markdown(response)
                    
                    # Display sources if available
                    if sources and self.chatbot.search_enabled:
                        self.render_sources(sources)
            
            # Store the response with sources
            st.session_state.messages.append({
                "role": "assistant", 
                "content": response,
                "sources": sources if self.chatbot.search_enabled else []
            })

    def run(self):
        """Run the Streamlit application"""
        self.setup_page()
        self.render_sidebar()
        
        # Main content area - full width since we removed right sidebar
        self.render_chat_interface()

def main():
    app = StreamlitChatApp()
    app.run()

if __name__ == "__main__":
    main()