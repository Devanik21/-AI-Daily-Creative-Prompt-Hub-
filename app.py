import streamlit as st
import datetime
import random
import google.generativeai as genai
import pyperclip

# --- Page Configuration ---
st.set_page_config(
    page_title="Daily Creative Prompt Hub",
    page_icon="🎨",
    layout="wide",
)

# --- CSS Styling ---
st.markdown("""
<style>
    body {
        color: #fff;
    }
    .main {
        background: linear-gradient(135deg, #232526 0%, #414345 100%);
    }
    .stApp {
        background-color: transparent;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #fff;
    }
    .stHeader, .stSubheader {
        color: #f0f0f0;
    }
    .prompt-container {
        background-color: #3a3a3a;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        color: #fff; /* Ensure text inside is white */
    }
    .prompt-container p em {
        color: #cccccc;
    }
    /* Make streamlit widgets dark */
    .stTextInput > div > div > input, .stTextArea > div > textarea {
        background-color: #3a3a3a;
        color: #fff;
    }
</style>
""", unsafe_allow_html=True)

# --- Title and Header ---
st.title("🎨 Daily Creative Prompt Hub")
st.header(f"📅 Prompt for {datetime.date.today().strftime('%B %d, %Y')}")

# --- Streak Counter ---
if 'streak' not in st.session_state:
    st.session_state.streak = 0
if 'last_prompt_date' not in st.session_state:
    st.session_state.last_prompt_date = None

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

# --- Prompts ---
prompts = {
    "✍️ Writing": [
        {"prompt": "Write a story about a character who wakes up with a new superpower.", "level": "Easy"},
        {"prompt": "Describe a world where gravity works differently.", "level": "Medium"},
        {"prompt": "Write a dialogue between two characters who have a secret.", "level": "Hard"},
    ],
    "🎨 Drawing": [
        {"prompt": "Draw a creature from your imagination.", "level": "Easy"},
        {"prompt": "Sketch a landscape from a dream.", "level": "Medium"},
        {"prompt": "Illustrate a scene from your favorite book.", "level": "Hard"},
    ],
    "💻 Coding": [
        {"prompt": "Code a simple game of tic-tac-toe.", "level": "Easy"},
        {"prompt": "Write a program that generates a random password.", "level": "Medium"},
        {"prompt": "Build a web scraper that extracts data from a website.", "level": "Hard"},
    ],
}

# --- Display Prompts ---
for category, prompt_list in prompts.items():
    with st.container():
        st.subheader(category)
        prompt = random.choice(prompt_list)
        st.markdown(f"""
        <div class="prompt-container">
            <p><strong>{prompt['prompt']}</strong></p>
            <p><em>Challenge Level: {prompt['level']}</em></p>
        </div>
        """, unsafe_allow_html=True)

# --- Gemini API Key ---
st.sidebar.title("🤖 Gemini API")
api_key = st.sidebar.text_input("Enter your Gemini API key", type="password")

# --- User Input and Feedback ---
st.header("🌟 Share Your Creation")
user_input = st.text_area("Paste your writing, a description of your drawing, or your code here.")

if st.button("Get Feedback"):
    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(f"Provide feedback on this creative work: {user_input}")
            st.subheader("💡 Gemini's Feedback")
            st.write(response.text)

            # --- Share Button ---
            share_text = f"My Creative Work:\n\n{user_input}\n\nGemini's Feedback:\n\n{response.text}"
            if st.button("Share to Clipboard"):
                pyperclip.copy(share_text)
                st.success("Copied to clipboard!")

        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.error("Please enter your Gemini API key in the sidebar.")
