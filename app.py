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
                    st.download_button(
                        label="Export to TXT",
                        data=response.text,
                        file_name="personalized_prompt.txt",
                        mime="text/plain"
                    )
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("API key is required for this feature.")

# --- Advanced AI Tools ---
with st.expander("🧠 Mind Map Generator"):
    mind_map_topic = st.text_input("Enter a topic for your mind map:")
    if st.button("Generate Mind Map"):
        if api_key and mind_map_topic:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.spinner("Generating mind map..."):
                    response = model.generate_content(f"Generate a markdown-formatted mind map for the topic: {mind_map_topic}")
                    st.markdown(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("API key and topic are required.")

with st.expander("📊 SWOT Analysis Generator"):
    swot_subject = st.text_input("Enter a business, product, or idea for SWOT analysis:")
    if st.button("Generate SWOT Analysis"):
        if api_key and swot_subject:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.spinner("Generating SWOT analysis..."):
                    response = model.generate_content(f"Generate a SWOT analysis (Strengths, Weaknesses, Opportunities, Threats) for: {swot_subject}")
                    st.markdown(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("API key and subject are required.")

with st.expander("📄 Code Documentation Writer"):
    code_to_doc = st.text_area("Paste your code here to generate documentation:")
    doc_lang = st.text_input("What programming language is this?", "python")
    if st.button("Generate Documentation"):
        if api_key and code_to_doc:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.spinner("Generating documentation..."):
                    response = model.generate_content(f"Generate documentation for the following {doc_lang} code: \n```\n{code_to_doc}\n```")
                    st.markdown(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("API key and code are required.")

with st.expander("🎤 Fictional Character Interviewer"):
    interviewer_char = st.text_area("Describe the fictional character you want to interview:")
    interviewer_question = st.text_input("What is your first question?")
    if st.button("Start Interview"):
        if api_key and interviewer_char and interviewer_question:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.spinner("Character is thinking..."):
                    response = model.generate_content(f"I am interviewing a fictional character. You are this character: '{interviewer_char}'. I will ask you questions. Respond as the character would. My first question is: {interviewer_question}")
                    st.write(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("API key, character description, and a question are required.")

with st.expander("🌙 Dream Interpreter"):
    dream_desc = st.text_area("Describe your dream in as much detail as possible:")
    if st.button("Interpret Dream"):
        if api_key and dream_desc:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.spinner("Interpreting your dream..."):
                    response = model.generate_content(f"Provide a psychological and symbolic interpretation of the following dream: {dream_desc}")
                    st.write(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("API key and dream description are required.")

with st.expander("⚖️ Ethical Dilemma Solver"):
    dilemma_desc = st.text_area("Describe an ethical dilemma:")
    if st.button("Analyze Dilemma"):
        if api_key and dilemma_desc:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.spinner("Analyzing the dilemma from multiple perspectives..."):
                    response = model.generate_content(f"Analyze the following ethical dilemma from utilitarian, deontological, and virtue ethics perspectives: {dilemma_desc}")
                    st.markdown(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("API key and dilemma description are required.")

with st.expander("🥗 Meal Plan Generator"):
    meal_diet = st.text_input("Any dietary requirements or preferences (e.g., vegan, low-carb)?", "None")
    meal_days = st.slider("Number of days for the meal plan:", 1, 14, 7)
    if st.button("Generate Meal Plan"):
        if api_key:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.spinner("Generating your meal plan..."):
                    response = model.generate_content(f"Create a {meal_days}-day meal plan (breakfast, lunch, dinner) with the following dietary needs: {meal_diet}. Include a grocery list.")
                    st.markdown(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("API key is required.")

with st.expander("💪 Personalized Fitness Challenge Creator"):
    challenge_goal = st.text_input("What is your fitness goal for this challenge?", "Improve overall fitness")
    challenge_duration = st.slider("Duration of the challenge (in days):", 7, 30, 30)
    if st.button("Create Challenge"):
        if api_key and challenge_goal:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.spinner("Creating your fitness challenge..."):
                    response = model.generate_content(f"Create a {challenge_duration}-day personalized fitness challenge for the goal: {challenge_goal}. The challenge should be progressive.")
                    st.markdown(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("API key and a goal are required.")

with st.expander("📱 Social Media Post Crafter"):
    social_topic = st.text_input("Topic for your social media posts:")
    social_platform = st.multiselect("Select platforms:", ["Twitter", "Facebook", "LinkedIn", "Instagram"])
    if st.button("Craft Posts"):
        if api_key and social_topic and social_platform:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.spinner("Crafting your posts..."):
                    response = model.generate_content(f"Craft social media posts about '{social_topic}' tailored for the following platforms: {', '.join(social_platform)}. Include relevant hashtags.")
                    st.markdown(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("API key, topic, and at least one platform are required.")

with st.expander("👨‍🏫 Lesson Plan Creator"):
    lesson_subject = st.text_input("Subject:")
    lesson_grade = st.text_input("Grade Level:")
    lesson_topic = st.text_input("Topic:")
    if st.button("Create Lesson Plan"):
        if api_key and lesson_subject and lesson_grade and lesson_topic:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.spinner("Creating your lesson plan..."):
                    response = model.generate_content(f"Create a detailed lesson plan for a {lesson_grade} class on the topic of '{lesson_topic}' in the subject of {lesson_subject}. Include objectives, activities, and assessment methods.")
                    st.markdown(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("All fields are required.")

with st.expander("🎮 Gamer Tag Generator"):
    gamer_theme = st.text_input("What theme for your gamer tag (e.g., 'cyberpunk', 'fantasy', 'space')?")
    if st.button("Generate Gamer Tags"):
        if api_key and gamer_theme:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.spinner("Generating gamer tags..."):
                    response = model.generate_content(f"Generate 10 unique and cool gamer tags with the theme: {gamer_theme}")
                    st.write(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("API key and theme are required.")

with st.expander("🗣️ Fictional Language Creator"):
    lang_concept = st.text_area("Describe the concept of your fictional language (e.g., 'spoken by tree-people, sounds like rustling leaves').")
    if st.button("Create Language Basics"):
        if api_key and lang_concept:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.spinner("Creating your language..."):
                    response = model.generate_content(f"Based on the concept '{lang_concept}', create a basic vocabulary of 20 words and simple grammatical rules for a new fictional language.")
                    st.markdown(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("API key and concept are required.")

with st.expander("✉️ Cover Letter Writer"):
    cover_job_desc = st.text_area("Paste the job description here:")
    cover_user_info = st.text_area("Paste your resume or key skills and experiences here:")
    if st.button("Write Cover Letter"):
        if api_key and cover_job_desc and cover_user_info:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.spinner("Writing your cover letter..."):
                    response = model.generate_content(f"Write a professional cover letter based on this job description: '{cover_job_desc}' and this user's information: '{cover_user_info}'.")
                    st.write(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("API key, job description, and user info are required.")

with st.expander("📦 Product Description Generator"):
    prod_name = st.text_input("Product Name:")
    prod_features = st.text_area("List the product's key features:")
    if st.button("Generate Description"):
        if api_key and prod_name and prod_features:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.spinner("Writing product description..."):
                    response = model.generate_content(f"Write a compelling e-commerce product description for '{prod_name}' with the following features: {prod_features}.")
                    st.write(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("All fields are required.")

with st.expander("🧘 Meditation Script Writer"):
    meditation_focus = st.text_input("What is the focus of the meditation (e.g., 'reducing anxiety', 'morning energy')?")
    meditation_duration = st.slider("Approximate duration (in minutes):", 1, 20, 5)
    if st.button("Write Meditation Script"):
        if api_key and meditation_focus:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.spinner("Writing your meditation script..."):
                    response = model.generate_content(f"Write a guided meditation script for a {meditation_duration}-minute session focused on {meditation_focus}.")
                    st.write(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("API key and focus are required.")

with st.expander("🏛️ Historical Figure Dialogue"):
    hist_fig1 = st.text_input("Historical Figure 1 (e.g., 'Albert Einstein')")
    hist_fig2 = st.text_input("Historical Figure 2 (e.g., 'Isaac Newton')")
    hist_topic = st.text_input("Topic of their conversation (e.g., 'the nature of gravity')")
    if st.button("Generate Historical Dialogue"):
        if api_key and hist_fig1 and hist_fig2 and hist_topic:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.spinner("Writing historical dialogue..."):
                    response = model.generate_content(f"Write a short, imagined dialogue between {hist_fig1} and {hist_fig2} about {hist_topic}. Capture their likely perspectives and personalities.")
                    st.write(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("All fields are required.")

with st.expander("👶 ELI5 (Explain Like I'm 5) Generator"):
    eli5_topic = st.text_input("Enter a complex topic to explain simply:")
    if st.button("Explain Like I'm 5"):
        if api_key and eli5_topic:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.spinner("Simplifying the topic..."):
                    response = model.generate_content(f"Explain the following topic like I'm 5 years old: {eli5_topic}")
                    st.write(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("API key and topic are required.")

with st.expander("⚔️ Debate Topic Generator"):
    debate_subject = st.text_input("Enter a subject for a debate (e.g., 'technology', 'education')")
    if st.button("Generate Debate Topic"):
        if api_key and debate_subject:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.spinner("Generating a debate topic..."):
                    response = model.generate_content(f"Generate a controversial debate topic related to {debate_subject}. Provide a brief for both the 'pro' and 'con' sides.")
                    st.markdown(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("API key and subject are required.")

# --- Prompt History ---

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
                    st.rerun()
                except Exception as e:
                    st.error(f"An error occurred: {e}")
        else: # User's turn
            user_addition = st.text_input("Your turn:", key="collab_user")
            if st.button("Add to Story") and user_addition:
                st.session_state.story.append(user_addition)
                st.rerun()

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

with st.expander("🌍 World Anvil"):
    world_input = st.text_area("Describe the basic concept of your world:")
    if st.button("Build World"):
        if api_key and world_input:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.spinner("Building your world..."):
                    response = model.generate_content(f"Expand this world concept with details on its history, cultures, and key locations: {world_input}")
                    st.write(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("API key and concept are required.")

with st.expander("👤 Character Backstory Generator"):
    char_concept = st.text_input("Character concept (e.g., 'a rogue with a heart of gold')")
    if st.button("Generate Backstory"):
        if api_key and char_concept:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.spinner("Writing backstory..."):
                    response = model.generate_content(f"Write a detailed backstory for this character: {char_concept}")
                    st.write(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("API key and concept are required.")

with st.expander("📜 Poetry Assistant"):
    poem_topic = st.text_input("Topic for your poem:")
    poem_type = st.selectbox("Type of poem:", ["Haiku", "Sonnet", "Free Verse"])
    if st.button("Write Poem"):
        if api_key and poem_topic:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.spinner("Writing your poem..."):
                    response = model.generate_content(f"Write a {poem_type} about {poem_topic}")
                    st.write(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("API key and topic are required.")

with st.expander("🎬 Scriptwriting Assistant"):
    script_scene = st.text_area("Describe the scene you want to write:")
    if st.button("Write Scene"):
        if api_key and script_scene:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.spinner("Writing your scene..."):
                    response = model.generate_content(f"Write a script scene based on this description: {script_scene}")
                    st.write(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("API key and scene description are required.")

with st.expander("📝 Blog Post Idea Generator"):
    blog_topic = st.text_input("Your blog's topic:")
    if st.button("Generate Ideas"):
        if api_key and blog_topic:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.spinner("Generating ideas..."):
                    response = model.generate_content(f"Generate 5 blog post ideas for a blog about {blog_topic}")
                    st.write(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("API key and topic are required.")

with st.expander("🗣️ Speech Writer"):
    speech_topic = st.text_input("Topic of your speech:")
    speech_tone = st.selectbox("Tone:", ["Inspirational", "Informative", "Humorous"])
    if st.button("Write Speech"):
        if api_key and speech_topic:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.spinner("Writing your speech..."):
                    response = model.generate_content(f"Write a short, {speech_tone} speech about {speech_topic}")
                    st.write(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("API key and topic are required.")

with st.expander("❓ Interview Question Generator"):
    job_role = st.text_input("Job role you're hiring for:")
    if st.button("Generate Questions"):
        if api_key and job_role:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.spinner("Generating questions..."):
                    response = model.generate_content(f"Generate 5 interview questions for a {job_role} position.")
                    st.write(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("API key and job role are required.")

with st.expander("📧 Email Responder"):
    email_context = st.text_area("Paste the email you need to respond to:")
    response_goal = st.text_input("What is the goal of your response?")
    if st.button("Draft Response"):
        if api_key and email_context and response_goal:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.spinner("Drafting your email..."):
                    response = model.generate_content(f"Draft an email response to the following email, with the goal of {response_goal}: {email_context}")
                    st.write(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("All fields are required.")

with st.expander("🤔 Analogy Generator"):
    concept = st.text_input("Concept to explain:")
    if st.button("Generate Analogy"):
        if api_key and concept:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.spinner("Generating an analogy..."):
                    response = model.generate_content(f"Generate an analogy to explain this concept: {concept}")
                    st.write(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("API key and concept are required.")

with st.expander("💡 Brainstorming Partner"):
    brainstorm_topic = st.text_input("What do you want to brainstorm about?")
    if st.button("Start Brainstorming"):
        if api_key and brainstorm_topic:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.spinner("Brainstorming..."):
                    response = model.generate_content(f"Let's brainstorm about {brainstorm_topic}. Here are some initial ideas:")
                    st.write(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("API key and topic are required.")

with st.expander("📚 Book Summary Generator"):
    book_title = st.text_input("Enter the title of a book:")
    if st.button("Summarize Book"):
        if api_key and book_title:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.spinner("Summarizing the book..."):
                    response = model.generate_content(f"Provide a concise summary of the book: {book_title}")
                    st.write(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("API key and book title are required.")

with st.expander("🌐 Language Translator"):
    text_to_translate = st.text_area("Enter text to translate:")
    target_language = st.text_input("Enter the target language (e.g., 'French', 'Japanese'):")
    if st.button("Translate"):
        if api_key and text_to_translate and target_language:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.spinner("Translating..."):
                    response = model.generate_content(f"Translate the following text to {target_language}: {text_to_translate}")
                    st.write(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("All fields are required.")

with st.expander("📰 News Article Summarizer"):
    article_url = st.text_input("Enter the URL of a news article:")
    if st.button("Summarize Article"):
        if api_key and article_url:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.spinner("Summarizing the article..."):
                    # Note: This requires the model to have web browsing capabilities.
                    # For this example, we'll just pass the URL and assume the model can access it.
                    response = model.generate_content(f"Summarize the news article at this URL: {article_url}")
                    st.write(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("API key and article URL are required.")

with st.expander("🍔 Recipe Generator"):
    ingredients = st.text_input("List the ingredients you have:")
    if st.button("Generate Recipe"):
        if api_key and ingredients:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.spinner("Creating a recipe..."):
                    response = model.generate_content(f"Generate a recipe using these ingredients: {ingredients}")
                    st.write(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("API key and ingredients are required.")

with st.expander("🏋️ Workout Plan Generator"):
    fitness_goal = st.text_input("What is your fitness goal (e.g., 'build muscle', 'lose weight')?")
    days_per_week = st.slider("How many days per week can you work out?", 1, 7, 3)
    if st.button("Generate Workout Plan"):
        if api_key and fitness_goal:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.spinner("Generating your workout plan..."):
                    response = model.generate_content(f"Create a {days_per_week}-day workout plan for someone whose goal is to {fitness_goal}.")
                    st.write(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("API key and fitness goal are required.")

with st.expander("✈️ Travel Itinerary Planner"):
    destination = st.text_input("Where do you want to go?")
    duration = st.slider("How many days will your trip be?", 1, 14, 5)
    if st.button("Plan Itinerary"):
        if api_key and destination:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.spinner("Planning your trip..."):
                    response = model.generate_content(f"Create a {duration}-day travel itinerary for a trip to {destination}.")
                    st.write(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("API key and destination are required.")

with st.expander("💼 Business Name Generator"):
    industry = st.text_input("What industry is your business in?")
    if st.button("Generate Business Names"):
        if api_key and industry:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.spinner("Generating business names..."):
                    response = model.generate_content(f"Generate 10 creative business names for a company in the {industry} industry.")
                    st.write(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("API key and industry are required.")

with st.expander("📣 Slogan Generator"):
    product = st.text_input("What is your product or brand?")
    if st.button("Generate Slogans"):
        if api_key and product:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.spinner("Generating slogans..."):
                    response = model.generate_content(f"Generate 5 catchy slogans for {product}.")
                    st.write(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("API key and product/brand are required.")

with st.expander("🎓 Learning Path Generator"):
    skill = st.text_input("What skill do you want to learn? (e.g., 'Python', 'Digital Marketing')")
    if st.button("Generate Learning Path"):
        if api_key and skill:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.spinner("Generating your learning path..."):
                    response = model.generate_content(f"Create a step-by-step learning path for someone who wants to learn {skill}.")
                    st.write(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("API key and skill are required.")

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
