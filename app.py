import streamlit as st
import datetime
import random
import google.generativeai as genai
import pyperclip
from gtts import gTTS
import io
from PIL import Image

# --- Page Configuration ---
st.set_page_config(
    page_title="Daily Creative Prompt Hub",
    page_icon="🎨",
    layout="wide",
)

# --- CSS Styling ---
st.markdown("""
<style>
    body { color: #fff; }
    .main { background: linear-gradient(135deg, #232526 0%, #414345 100%); }
    .stApp { background-color: transparent; }
    h1, h2, h3, h4, h5, h6 { color: #fff; }
    .stHeader, .stSubheader { color: #f0f0f0; }
    .prompt-container {
        background-color: #3a3a3a;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        color: #fff;
    }
    .prompt-container p em { color: #cccccc; }
    .stTextInput > div > div > input, .stTextArea > div > textarea {
        background-color: #3a3a3a;
        color: #fff;
    }
</style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if 'streak' not in st.session_state: st.session_state.streak = 0
if 'last_prompt_date' not in st.session_state: st.session_state.last_prompt_date = None
if 'completed_prompts' not in st.session_state: st.session_state.completed_prompts = 0
if 'badges' not in st.session_state: st.session_state.badges = []
if 'prompt_history' not in st.session_state: st.session_state.prompt_history = {}
if 'gallery' not in st.session_state: st.session_state.gallery = []

# --- Gemini API Key ---
st.sidebar.title("🤖 Gemini API")
api_key = st.sidebar.text_input("Enter your Gemini API key", type="password")

# --- User Profile & Gamification ---
st.sidebar.header("👤 User Profile")
today = datetime.date.today()
if st.session_state.last_prompt_date:
    if (today - st.session_state.last_prompt_date).days == 1:
        st.session_state.streak += 1
    elif (today - st.session_state.last_prompt_date).days > 1:
        st.session_state.streak = 1
else:
    st.session_state.streak = 1
st.session_state.last_prompt_date = today

st.sidebar.metric("🔥 Streak", f"{st.session_state.streak} days")
st.sidebar.metric("✅ Prompts Completed", st.session_state.completed_prompts)

if st.session_state.streak >= 5 and "5-Day Streak" not in st.session_state.badges:
    st.session_state.badges.append("5-Day Streak")
if st.session_state.completed_prompts >= 10 and "10 Prompts Completed" not in st.session_state.badges:
    st.session_state.badges.append("10 Prompts Completed")

st.sidebar.subheader("🏆 Badges")
for badge in st.session_state.badges:
    st.sidebar.write(f"- {badge}")

# --- Themed Weeks ---
themes = {
    1: "Sci-Fi Future", 2: "Fantasy Realms", 3: "Mystery & Detective", 4: "Cyberpunk City"
}
week_of_year = datetime.date.today().isocalendar()[1]
theme = themes.get(week_of_year % len(themes) + 1, "General")
st.header(f"🌌 Weekly Theme: {theme}")

# --- Prompts ---
prompts = { # Expanded prompts for themes
    "✍️ Writing": [
        {"prompt": "An android discovers it can dream.", "level": "Easy", "theme": "Sci-Fi Future"},
        {"prompt": "A dragon's last egg is stolen.", "level": "Medium", "theme": "Fantasy Realms"},
        {"prompt": "A detective finds a strange symbol at a crime scene.", "level": "Hard", "theme": "Mystery & Detective"},
    ],
    "🎨 Drawing": [
        {"prompt": "A bustling alien marketplace.", "level": "Easy", "theme": "Sci-Fi Future"},
        {"prompt": "An enchanted forest with glowing flora.", "level": "Medium", "theme": "Fantasy Realms"},
        {"prompt": "A noir-style city in perpetual rain.", "level": "Hard", "theme": "Mystery & Detective"},
    ],
    "💻 Coding": [
        {"prompt": "A script to simulate a starship's dashboard.", "level": "Easy", "theme": "Sci-Fi Future"},
        {"prompt": "A fantasy RPG character generator.", "level": "Medium", "theme": "Fantasy Realms"},
        {"prompt": "A program to decode secret messages.", "level": "Hard", "theme": "Mystery & Detective"},
    ],
}

# --- Difficulty Filter ---
st.sidebar.header("⚙️ Options")
difficulty = st.sidebar.selectbox("Filter by Difficulty", ["All", "Easy", "Medium", "Hard"])

# --- Display Prompts ---
st.title("🎨 Daily Creative Prompt Hub")
for category, prompt_list in prompts.items():
    with st.container():
        st.subheader(category)
        filtered_prompts = [p for p in prompt_list if difficulty == "All" or p["level"] == difficulty]
        if not filtered_prompts:
            st.write("No prompts match the selected difficulty.")
            continue
        prompt = random.choice(filtered_prompts)
        st.session_state.prompt_history.setdefault(str(today), []).append(prompt)

        with st.container():
            st.markdown(f"<div class='prompt-container'><p><strong>{prompt['prompt']}</strong></p><p><em>Challenge Level: {prompt['level']}</em></p></div>", unsafe_allow_html=True)
            # --- Text-to-Speech ---
            tts_fp = io.BytesIO()
            tts = gTTS(prompt['prompt'], lang='en')
            tts.write_to_fp(tts_fp)
            st.audio(tts_fp)

# --- User Input and Feedback ---
st.header("🌟 Share Your Creation")
if category == "🎨 Drawing":
    uploaded_file = st.file_uploader("Upload your drawing", type=["png", "jpg", "jpeg"])
    user_input = st.text_area("Or describe your drawing here")
else:
    user_input = st.text_area("Paste your writing or code here.")
    uploaded_file = None

if st.button("Get Feedback"):
    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            if uploaded_file:
                img = Image.open(uploaded_file)
                response = model.generate_content([user_input, img])
            else:
                response = model.generate_content(f"Provide feedback on this creative work: {user_input}")
            
            st.subheader("💡 Gemini's Feedback")
            st.write(response.text)
            st.session_state.completed_prompts += 1

            # --- Share and Export ---
            share_text = f"My Work:\n{user_input}\n\nFeedback:\n{response.text}"
            st.download_button("Export to Markdown", share_text, file_name="creation.md")
            if st.button("Share to Gallery"):
                st.session_state.gallery.append({"work": user_input, "feedback": response.text, "image": uploaded_file})
                st.success("Shared to the gallery!")

        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.error("Please enter your Gemini API key.")

# --- Personalized Prompts ---
with st.expander("✨ Get a Personalized Prompt"):
    topic = st.text_input("Enter a topic (e.g., 'space opera', 'haunted house')", key="personalized_prompt_input")
    if st.button("Generate Prompt"):
        if api_key:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.spinner("Generating your personalized prompt..."):
                    response = model.generate_content(f"Generate a creative prompt about: {topic}")
                    st.write(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("API key is required for this feature.")

# --- Advanced AI Tools ---
with st.expander("🔬 Advanced AI Critiques"):
    critique_type = st.selectbox("Select Critique Type", ["Plot Hole Analysis", "Character Arc Review", "Code Efficiency Check"])
    critique_input = st.text_area("Paste your text or code for critique:")
    if st.button("Get Critique"):
        if api_key and critique_input:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.spinner("Analyzing..."):
                    response = model.generate_content(f"Provide a {critique_type} for the following: {critique_input}")
                    st.write(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("API key and input are required.")

with st.expander("💡 Idea Expander"):
    idea_input = st.text_input("Enter a simple idea (e.g., 'a talking cat')")
    if st.button("Expand Idea"):
        if api_key and idea_input:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.spinner("Expanding your idea..."):
                    response = model.generate_content(f"Expand this idea into a detailed concept with world-building notes: {idea_input}")
                    st.write(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("API key and input are required.")

with st.expander("✍️ Style Transfer"):
    style_input = st.text_area("Paste your text here:")
    style_author = st.text_input("Enter an author's name (e.g., 'Ernest Hemingway')")
    if st.button("Transfer Style"):
        if api_key and style_input and style_author:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.spinner("Transferring style..."):
                    response = model.generate_content(f"Rewrite the following text in the style of {style_author}: {style_input}")
                    st.write(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("All fields are required.")

with st.expander("🤝 Collaborative Storytelling"):
    if 'story' not in st.session_state:
        st.session_state.story = []
    
    story_start = st.text_input("Start a story:", key="collab_start")
    if st.button("Begin Story") and story_start:
        st.session_state.story = [story_start]

    if st.session_state.story:
        for part in st.session_state.story:
            st.write(part)
        
        if len(st.session_state.story) % 2 != 0: # AI's turn
            with st.spinner("AI is thinking..."):
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    response = model.generate_content(f"Continue this story: {' '.join(st.session_state.story)}")
                    st.session_state.story.append(response.text)
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"An error occurred: {e}")
        else: # User's turn
            user_addition = st.text_input("Your turn:", key="collab_user")
            if st.button("Add to Story") and user_addition:
                st.session_state.story.append(user_addition)
                st.experimental_rerun()

with st.expander("💻 Code Refactoring Suggestions"):
    code_input = st.text_area("Paste your code here for refactoring suggestions:")
    if st.button("Get Suggestions"):
        if api_key and code_input:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.spinner("Generating suggestions..."):
                    response = model.generate_content(f"Provide code refactoring suggestions for the following code: {code_input}")
                    st.code(response.text, language='python')
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("API key and code are required.")

with st.expander("🎵 Music/Ambiance Suggester"):
    ambiance_input = st.text_area("Describe the scene or mood:")
    if st.button("Get Ambiance"):
        if api_key and ambiance_input:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.spinner("Finding the perfect sound..."):
                    response = model.generate_content(f"Suggest music or ambiance for the following scene: {ambiance_input}")
                    st.write(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("API key and description are required.")

with st.expander("🏷️ Title Generator"):
    title_input = st.text_area("Paste the text of your work here:")
    if st.button("Generate Titles"):
        if api_key and title_input:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.spinner("Generating titles..."):
                    response = model.generate_content(f"Generate 5 catchy titles for the following work: {title_input}")
                    st.write(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("API key and text are required.")

with st.expander("💬 Character Dialogue Generator"):
    char1 = st.text_input("Character 1 (e.g., 'a grumpy dwarf')")
    char2 = st.text_input("Character 2 (e.g., 'an optimistic elf')")
    situation = st.text_input("Situation (e.g., 'they are lost in a forest')")
    if st.button("Generate Dialogue"):
        if api_key and char1 and char2 and situation:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.spinner("Writing dialogue..."):
                    response = model.generate_content(f"Write a short dialogue between {char1} and {char2} in this situation: {situation}")
                    st.write(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("All fields are required.")

with st.expander("💥 Plot Twist Generator"):
    plot_input = st.text_area("Summarize your plot so far:")
    if st.button("Generate Twist"):
        if api_key and plot_input:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.spinner("Thinking of a twist..."):
                    response = model.generate_content(f"Generate a surprising plot twist for this story: {plot_input}")
                    st.write(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("API key and plot summary are required.")

with st.expander("🎨 Visual Palette Generator"):
    palette_input = st.text_area("Describe the mood or theme of your artwork:")
    if st.button("Generate Palette"):
        if api_key and palette_input:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.spinner("Generating a palette..."):
                    response = model.generate_content(f"Generate a color palette (with hex codes) for this theme: {palette_input}")
                    st.write(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("API key and description are required.")

# --- Prompt History ---
with st.expander("📜 Prompt History"):
    for date_str, prompts_of_day in list(st.session_state.prompt_history.items())[-5:]:
        st.subheader(date_str)
        for p in prompts_of_day:
            st.write(f"- {p['prompt']} ({p['level']})")

# --- Community Gallery ---
with st.expander("🖼️ Community Gallery"):
    if not st.session_state.gallery:
        st.write("The gallery is empty. Be the first to share!")
    for item in st.session_state.gallery:
        st.markdown("***")
        if item['image']:
            st.image(item['image'])
        st.write(f"**Work:** {item['work']}")
        st.write(f"**Feedback:** {item['feedback']}")

