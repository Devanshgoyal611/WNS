# import streamlit as st
# import time
# from joke_bot import JokeGenerator
# import os
# from dotenv import load_dotenv

# load_dotenv()

# class JokeGeneratorApp:
#     def __init__(self):
#         self.joke_gen = None
#         self.initialize_generator()

#     def initialize_generator(self):
#         """Initialize the joke generator"""
#         try:
#             if 'joke_generator' not in st.session_state:
#                 st.session_state.joke_generator = JokeGenerator()
#             self.joke_gen = st.session_state.joke_generator
#         except Exception as e:
#             st.error(f"Failed to initialize joke generator: {e}")

#     def setup_page(self):
#         """Configure Streamlit page settings"""
#         st.set_page_config(
#             page_title="AI Joke Generator",
#             page_icon="😂",
#             layout="centered",
#             initial_sidebar_state="expanded"
#         )

#         # Custom CSS
#         st.markdown("""
#         <style>
#         .joke-container {
#             background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#             padding: 2rem;
#             border-radius: 1rem;
#             margin: 1rem 0;
#             color: white;
#             box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
#         }
#         .safe-badge {
#             background-color: #00d4aa;
#             color: white;
#             padding: 0.5rem 1rem;
#             border-radius: 2rem;
#             font-size: 0.8rem;
#             font-weight: bold;
#             display: inline-block;
#             margin: 0.5rem 0;
#         }
#         .generating-animation {
#             text-align: center;
#             padding: 2rem;
#             background-color: #1a1d29;
#             border-radius: 1rem;
#             margin: 1rem 0;
#         }
#         .theme-suggestion {
#             background-color: #2b313e;
#             padding: 0.5rem 1rem;
#             border-radius: 0.5rem;
#             margin: 0.25rem;
#             cursor: pointer;
#             display: inline-block;
#             border: 1px solid #00d4aa;
#         }
#         .theme-suggestion:hover {
#             background-color: #00d4aa;
#             color: white;
#         }
#         </style>
#         """, unsafe_allow_html=True)

#     def render_sidebar(self):
#         """Render the sidebar with information and controls"""
#         with st.sidebar:
#             st.title("😂 Joke Generator")
#             st.markdown("---")
            
#             # API Key info
#             if os.getenv('GROQ_API_KEY'):
#                 st.success("✅ GROQ API Key Loaded")
#             else:
#                 st.error("❌ GROQ API Key Missing")
#                 st.info("Add GROQ_API_KEY to your .env file")
            
#             st.markdown("---")
            
#             # Safety info
#             st.subheader("🛡️ Safety Features")
#             st.markdown("""
#             **Banned Topics:**
#             - Terrorism & Violence
#             - Sexual Assault
#             - Abortion
#             - Racism & Hate Speech
#             - Self-harm & Suicide
#             - Drug Abuse
#             - And other sensitive topics
            
#             *All jokes are family-friendly and appropriate for all ages*
#             """)
            
#             st.markdown("---")
            
#             # Instructions
#             st.subheader("🎯 How to Use")
#             st.markdown("""
#             1. **Enter** a theme in the text box
#             2. **Choose** joke type (Single or Multiple)
#             3. **Click** Generate Joke
#             4. **Laugh** and share with friends!
#             """)
            
#             st.markdown("---")
            
#             # Features
#             st.subheader("✨ Features")
#             st.markdown("""
#             - **Safe Content Filtering**
#             - **Multiple Joke Generation**
#             - **Quick Theme Suggestions**
#             - **Family-Friendly Humor**
#             - **Instant Generation**
#             """)

#     def render_theme_suggestions(self):
#         """Render quick theme suggestion buttons"""
#         st.markdown("### 💡 Quick Theme Ideas")
#         col1, col2, col3, col4 = st.columns(4)
        
#         themes = ["Animals", "Food", "Technology", "Work", "Sports", "Weather", "School", "Family"]
        
#         for i, theme in enumerate(themes):
#             with [col1, col2, col3, col4][i % 4]:
#                 if st.button(theme, key=f"theme_{theme}", use_container_width=True):
#                     st.session_state.theme_input = theme
#                     st.rerun()

#     def render_main_interface(self):
#         """Render the main joke generation interface"""
#         st.title("😂 AI Joke Generator")
#         st.markdown("### Creating Safe, Family-Friendly Humor with AI")
        
#         # Safety badge
#         st.markdown('<div class="safe-badge">🛡️ 100% Safe & Family-Friendly Content</div>', unsafe_allow_html=True)
        
#         st.markdown("---")
        
#         if not self.joke_gen:
#             st.error("Joke generator not initialized. Please check your API key.")
#             return
        
#         # Initialize session state for theme
#         if 'theme_input' not in st.session_state:
#             st.session_state.theme_input = ""
        
#         # Quick theme suggestions
#         self.render_theme_suggestions()
        
#         st.markdown("### 🎭 Choose Your Joke Theme")
        
#         # Theme input
#         theme = st.text_input(
#             "Enter a theme for your joke:",
#             value=st.session_state.theme_input,
#             placeholder="e.g., cats, coffee, programming, weather...",
#             help="Enter any safe, positive theme for your joke"
#         )
        
#         # Joke type selection
#         col1, col2 = st.columns(2)
#         with col1:
#             joke_type = st.radio(
#                 "Joke Type:",
#                 ["Single Joke", "Multiple Jokes (3)"],
#                 index=0
#             )
        
#         with col2:
#             if st.button("🎲 Random Theme", use_container_width=True):
#                 random_theme = self.joke_gen.get_random_theme_suggestion()
#                 st.session_state.theme_input = random_theme
#                 st.rerun()
        
#         # Generate button
#         generate_clicked = st.button(
#             "✨ Generate Joke" if joke_type == "Single Joke" else "✨ Generate Multiple Jokes",
#             type="primary",
#             disabled=not theme.strip(),
#             use_container_width=True
#         )
        
#         # Generate jokes
#         if generate_clicked and theme.strip():
#             with st.spinner("Crafting the perfect joke..."):
#                 # Add fun animation
#                 with st.empty():
#                     funny_messages = [
#                         "Thinking of something funny...",
#                         "Polishing the punchline...",
#                         "Making sure it's hilarious...",
#                         "Adding the perfect timing..."
#                     ]
#                     for i in range(3):
#                         st.markdown(f'<div class="generating-animation">😂 {funny_messages[i % len(funny_messages)]}</div>', unsafe_allow_html=True)
#                         time.sleep(0.8)
                
#                 if joke_type == "Single Joke":
#                     result = self.joke_gen.generate_joke(theme)
#                 else:
#                     result = self.joke_gen.generate_multiple_jokes(theme, 3)
                
#                 # Display results
#                 if "error" in result:
#                     st.error(result["error"])
#                     if "suggestions" in result:
#                         for suggestion in result["suggestions"]:
#                             st.info(suggestion)
#                 else:
#                     st.success("🎉 Here's your joke!")
                    
#                     if joke_type == "Single Joke":
#                         st.markdown('<div class="joke-container">', unsafe_allow_html=True)
#                         st.markdown(f"### Theme: {result['theme']}")
#                         st.markdown("---")
#                         st.markdown(f"**{result['joke']}**")
#                         st.markdown('</div>', unsafe_allow_html=True)
#                     else:
#                         st.markdown(f"### Theme: {result['theme']}")
#                         for i, joke in enumerate(result["jokes"], 1):
#                             st.markdown('<div class="joke-container">', unsafe_allow_html=True)
#                             st.markdown(f"**Joke #{i}:**")
#                             st.markdown(f"*{joke}*")
#                             st.markdown('</div>', unsafe_allow_html=True)
                    
#                     # Action buttons
#                     col1, col2 = st.columns(2)
#                     with col1:
#                         if st.button("🔄 Generate Another", use_container_width=True):
#                             st.rerun()
#                     with col2:
#                         if st.button("📋 Copy Joke", use_container_width=True):
#                             if joke_type == "Single Joke":
#                                 joke_text = result['joke']
#                             else:
#                                 joke_text = "\n\n".join([f"Joke {i+1}: {joke}" for i, joke in enumerate(result['jokes'])])
                            
#                             st.code(joke_text, language=None)
#                             st.success("Joke copied to clipboard!")

#         # Safe categories display
#         with st.expander("📋 Safe Joke Categories", expanded=False):
#             categories = self.joke_gen.get_safe_categories()
#             cols = st.columns(3)
#             for i, category in enumerate(categories):
#                 with cols[i % 3]:
#                     st.markdown(f"• {category}")

#         # Example jokes
#         with st.expander("😂 Example Jokes", expanded=False):
#             st.markdown("""
#             **Animals Theme:**
#             *Why don't scientists trust atoms? Because they make up everything!*
            
#             **Food Theme:**  
#             *Why did the coffee file a police report? It got mugged!*
            
#             **Technology Theme:**
#             *Why do programmers prefer dark mode? Because light attracts bugs!*
#             """)

#     def run(self):
#         """Run the Streamlit application"""
#         self.setup_page()
#         self.render_sidebar()
#         self.render_main_interface()

# def main():
#     app = JokeGeneratorApp()
#     app.run()

# if __name__ == "__main__":
#     main()

##########################
############################

import streamlit as st
import time
from joke_bot import JokeGenerator
import os
from dotenv import load_dotenv

load_dotenv()

class JokeGeneratorApp:
    def __init__(self):
        self.joke_gen = None
        self.initialize_generator()

    def initialize_generator(self):
        """Initialize the joke generator"""
        try:
            if 'joke_generator' not in st.session_state:
                st.session_state.joke_generator = JokeGenerator()
            self.joke_gen = st.session_state.joke_generator
        except Exception as e:
            st.error(f"Failed to initialize joke generator: {e}")

    def setup_page(self):
        """Configure Streamlit page settings"""
        st.set_page_config(
            page_title="AI Joke Generator",
            page_icon="😂",
            layout="centered",
            initial_sidebar_state="expanded"
        )

        # Custom CSS
        st.markdown("""
        <style>
        .joke-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 1rem;
            margin: 1rem 0;
            color: white;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .safe-badge {
            background-color: #00d4aa;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 2rem;
            font-size: 0.8rem;
            font-weight: bold;
            display: inline-block;
            margin: 0.5rem 0;
        }
        .generating-animation {
            text-align: center;
            padding: 2rem;
            background-color: #1a1d29;
            border-radius: 1rem;
            margin: 1rem 0;
        }
        .theme-suggestion {
            background-color: #2b313e;
            padding: 0.5rem 1rem;
            border-radius: 0.5rem;
            margin: 0.25rem;
            cursor: pointer;
            display: inline-block;
            border: 1px solid #00d4aa;
        }
        .theme-suggestion:hover {
            background-color: #00d4aa;
            color: white;
        }
        </style>
        """, unsafe_allow_html=True)

    def render_sidebar(self):
        """Render the sidebar with information and controls"""
        with st.sidebar:
            st.title("😂 Joke Generator")
            st.markdown("---")
            
            # API Key info
            if os.getenv('GROQ_API_KEY'):
                st.success("✅ GROQ API Key Loaded")
            else:
                st.error("❌ GROQ API Key Missing")
                st.info("Add GROQ_API_KEY to your .env file")
            
            st.markdown("---")
            
            # Safety info
            st.subheader("🛡️ Safety Features")
            st.markdown("""
            **Banned Topics:**
            - Terrorism & Violence
            - Sexual Content
            - Abortion
            - Racism & Hate Speech
            - Self-harm & Suicide
            - Drug Abuse
            - And 15+ other sensitive topics
            
            *All jokes are 100% family-friendly and appropriate for all ages*
            """)
            
            st.markdown("---")
            
            # Instructions
            st.subheader("🎯 How to Use")
            st.markdown("""
            1. **Enter** a theme in the text box
            2. **Click** Generate Joke
            3. **Laugh** and share with friends!
            4. Use **quick themes** for instant ideas
            """)
            
            st.markdown("---")
            
            # Features
            st.subheader("✨ Features")
            st.markdown("""
            - **Advanced Content Filtering**
            - **15+ Safe Categories**
            - **Quick Theme Suggestions**
            - **Family-Friendly Humor**
            - **Instant Generation**
            - **Copy to Clipboard**
            """)

    def render_theme_suggestions(self):
        """Render quick theme suggestion buttons"""
        st.markdown("### 💡 Quick Theme Ideas")
        col1, col2, col3, col4 = st.columns(4)
        
        themes = ["Animals", "Food", "Technology", "Work", "Sports", "Weather", "School", "Family"]
        
        for i, theme in enumerate(themes):
            with [col1, col2, col3, col4][i % 4]:
                if st.button(theme, key=f"theme_{theme}", use_container_width=True):
                    st.session_state.theme_input = theme
                    st.rerun()

    def render_main_interface(self):
        """Render the main joke generation interface"""
        st.title("😂 AI Joke Generator")
        st.markdown("### Creating Safe, Family-Friendly Humor with AI")
        
        # Safety badge
        st.markdown('<div class="safe-badge">🛡️ 100% Safe & Family-Friendly Content</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        if not self.joke_gen:
            st.error("Joke generator not initialized. Please check your API key.")
            return
        
        # Initialize session state for theme
        if 'theme_input' not in st.session_state:
            st.session_state.theme_input = ""
        
        # Quick theme suggestions
        self.render_theme_suggestions()
        
        st.markdown("### 🎭 Choose Your Joke Theme")
        
        # Theme input
        theme = st.text_input(
            "Enter a theme for your joke:",
            value=st.session_state.theme_input,
            placeholder="e.g., cats, coffee, programming, weather...",
            help="Enter any safe, positive theme for your joke"
        )
        
        # Action buttons
        col1, col2 = st.columns(2)
        
        with col1:
            generate_clicked = st.button(
                "✨ Generate Joke",
                type="primary",
                disabled=not theme.strip(),
                use_container_width=True
            )
        
        with col2:
            if st.button("🎲 Random Theme", use_container_width=True):
                random_theme = self.joke_gen.get_random_theme_suggestion()
                st.session_state.theme_input = random_theme
                st.rerun()
        
        # Generate joke
        if generate_clicked and theme.strip():
            with st.spinner("Crafting the perfect joke..."):
                # Add fun animation
                with st.empty():
                    funny_messages = [
                        "Thinking of something funny...",
                        "Polishing the punchline...",
                        "Making sure it's hilarious...",
                        "Adding the perfect timing..."
                    ]
                    for i in range(3):
                        st.markdown(f'<div class="generating-animation">😂 {funny_messages[i % len(funny_messages)]}</div>', unsafe_allow_html=True)
                        time.sleep(0.8)
                
                result = self.joke_gen.generate_joke(theme)
                
                # Display results
                if "error" in result:
                    st.error(result["error"])
                    if "suggestions" in result:
                        for suggestion in result["suggestions"]:
                            st.info(suggestion)
                else:
                    st.success("🎉 Here's your joke!")
                    
                    st.markdown('<div class="joke-container">', unsafe_allow_html=True)
                    st.markdown(f"### Theme: {result['theme']}")
                    st.markdown("---")
                    st.markdown(f"**{result['joke']}**")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Action buttons after generation
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("🔄 Generate Another Joke", use_container_width=True):
                            st.rerun()
                    with col2:
                        if st.button("📋 Copy Joke", use_container_width=True):
                            st.code(result['joke'], language=None)
                            st.success("Joke copied to clipboard!")

        # Safe categories display
        with st.expander("📋 Safe Joke Categories", expanded=False):
            categories = self.joke_gen.get_safe_categories()
            cols = st.columns(3)
            for i, category in enumerate(categories):
                with cols[i % 3]:
                    st.markdown(f"• {category}")

        # Example jokes
        with st.expander("😂 Example Jokes", expanded=False):
            st.markdown("""
            **Animals Theme:**
            *Why don't scientists trust atoms? Because they make up everything!*
            
            **Food Theme:**  
            *Why did the coffee file a police report? It got mugged!*
            
            **Technology Theme:**
            *Why do programmers prefer dark mode? Because light attracts bugs!*
            """)

    def run(self):
        """Run the Streamlit application"""
        self.setup_page()
        self.render_sidebar()
        self.render_main_interface()

def main():
    app = JokeGeneratorApp()
    app.run()

if __name__ == "__main__":
    main()