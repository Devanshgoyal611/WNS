import streamlit as st
import time
from bot import StoryGenerator
import os
from dotenv import load_dotenv

load_dotenv()

class StoryGeneratorApp:
    def __init__(self):
        self.story_gen = None
        self.initialize_generator()

    def initialize_generator(self):
        """Initialize the story generator"""
        try:
            if 'story_generator' not in st.session_state:
                st.session_state.story_generator = StoryGenerator()
            self.story_gen = st.session_state.story_generator
        except Exception as e:
            st.error(f"Failed to initialize story generator: {e}")

    def setup_page(self):
        """Configure Streamlit page settings"""
        st.set_page_config(
            page_title="AI Story Generator",
            page_icon="📖",
            layout="wide",
            initial_sidebar_state="expanded"
        )

        # Custom CSS
        st.markdown("""
        <style>
        .story-container {
            background-color: #1a1d29;
            padding: 2rem;
            border-radius: 0.5rem;
            border-left: 5px solid #ffd700;
            margin: 1rem 0;
        }
        .idea-feedback {
            background-color: #2b313e;
            padding: 1.5rem;
            border-radius: 0.5rem;
            border-left: 5px solid #00d4aa;
            margin: 1rem 0;
        }
        .generating-animation {
            text-align: center;
            padding: 2rem;
        }
        </style>
        """, unsafe_allow_html=True)

    def render_sidebar(self):
        """Render the sidebar with information and controls"""
        with st.sidebar:
            st.title("📖 Story Generator")
            st.markdown("---")
            
            # API Key info
            if os.getenv('GROQ_API_KEY'):
                st.success("✅ GROQ API Key Loaded")
            else:
                st.error("❌ GROQ API Key Missing")
                st.info("Add GROQ_API_KEY to your .env file")
            
            st.markdown("---")
            
            # Instructions
            st.subheader("🎯 How to Use")
            st.markdown("""
            1. **Describe** your story idea in the text area
            2. **Select** a genre from the dropdown
            3. **Choose** the desired length
            4. **Click** Generate Story
            5. **Read** and enjoy your unique story!
            """)
            
            st.markdown("---")
            
            # Features
            st.subheader("✨ Features")
            st.markdown("""
            - **16+ Genres** to choose from
            - **3 Length Options**
            - **Creative AI** powered by Llama3
            - **Instant Generation**
            - **Idea Analysis**
            """)
            
            st.markdown("---")
            
            # Model info
            st.subheader("🔧 Technical Info")
            st.markdown("""
            **Model:** Llama3 8B 8192
            **Provider:** Groq
            **AI:** Creative Story Generation
            """)

    def render_main_interface(self):
        """Render the main story generation interface"""
        st.title("📖 AI Story Generator")
        st.markdown("Transform your ideas into captivating stories with AI-powered creativity")
        st.markdown("---")
        
        if not self.story_gen:
            st.error("Story generator not initialized. Please check your API key.")
            return
        
        # Input section
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("🎭 Your Story Idea")
            story_idea = st.text_area(
                "Describe what you want in your story:",
                placeholder="Example: A young wizard discovers a hidden magical world in his grandmother's attic...",
                height=150,
                help="Be as descriptive as you want about characters, setting, or plot elements"
            )
        
        with col2:
            st.subheader("⚙️ Story Settings")
            
            genre = st.selectbox(
                "Select Genre:",
                options=self.story_gen.get_genres(),
                index=0,
                help="Choose the genre for your story"
            )
            
            length = st.selectbox(
                "Story Length:",
                options=self.story_gen.get_length_options(),
                index=1,  # Default to Medium
                help="Choose how long you want the story to be"
            )
            
            # Show length description
            length_desc = self.story_gen.length_mappings.get(length, "500-800 words")
            st.info(f"📏 **{length}**: {length_desc}")

        # Action buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            generate_clicked = st.button(
                "✨ Generate Story",
                type="primary",
                use_container_width=True,
                disabled=not story_idea.strip()
            )
        
        # Idea analysis section
        if story_idea.strip() and len(story_idea) > 10:
            with st.expander("💡 Get Feedback on Your Story Idea", expanded=False):
                if st.button("Analyze Idea", key="analyze_idea"):
                    with st.spinner("Analyzing your story idea..."):
                        feedback = self.story_gen.analyze_story_idea(story_idea)
                        st.markdown('<div class="idea-feedback">', unsafe_allow_html=True)
                        st.markdown("### 💡 Idea Analysis")
                        st.markdown(feedback)
                        st.markdown('</div>', unsafe_allow_html=True)

        # Generate story
        if generate_clicked and story_idea.strip():
            with st.spinner(f"Creating your {genre} story... This may take a moment."):
                # Add a simple animation
                with st.empty():
                    for i in range(3):
                        st.markdown(f'<div class="generating-animation">✨ Weaving your story... {"." * (i + 1)}</div>', unsafe_allow_html=True)
                        time.sleep(0.5)
                
                result = self.story_gen.generate_story(story_idea, genre, length)
                
                if "error" in result:
                    st.error(result["error"])
                else:
                    # Display the generated story
                    st.markdown("---")
                    st.success("🎉 Your story is ready!")
                    
                    # Story metadata
                    col1, col2 = st.columns(2)
                    with col1:
                        st.info(f"**Genre:** {result['genre']}")
                    with col2:
                        st.info(f"**Length:** {result['length']} ({result['word_range']})")
                    
                    # The story content
                    st.markdown('<div class="story-container">', unsafe_allow_html=True)
                    st.markdown("### 📖 Your Generated Story")
                    st.markdown("---")
                    st.markdown(result['story'])
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Additional actions
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("🔄 Generate Another Story", use_container_width=True):
                            st.rerun()
                    with col2:
                        # Copy to clipboard functionality
                        st.download_button(
                            label="💾 Download Story",
                            data=result['story'],
                            file_name=f"{genre.lower()}_story.txt",
                            mime="text/plain",
                            use_container_width=True
                        )

        # Example section for inspiration
        with st.expander("💡 Need Inspiration? Click here for story ideas", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Fantasy**")
                st.caption("A blacksmith's apprentice discovers their ability to talk to magical weapons")
            
            with col2:
                st.markdown("**Science Fiction**")
                st.caption("The first AI to develop emotions must hide them from its human creators")
            
            with col3:
                st.markdown("**Mystery**")
                st.caption("A librarian finds coded messages in old books that predict future events")

    def run(self):
        """Run the Streamlit application"""
        self.setup_page()
        self.render_sidebar()
        self.render_main_interface()

def main():
    app = StoryGeneratorApp()
    app.run()

if __name__ == "__main__":
    main()