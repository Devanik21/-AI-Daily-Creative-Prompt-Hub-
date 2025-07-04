import streamlit as st
import datetime
import random
import google.generativeai as genai

st.title("Daily Creative Prompt Hub")

# Get the current date
today = datetime.date.today()

# Set the random seed based on the current date
random.seed(today.toordinal())

# Prompts
writing_prompts = [
    "Write a story about a character who wakes up with a new superpower.",
    "Describe a world where gravity works differently.",
    "Write a dialogue between two characters who have a secret.",
]

drawing_prompts = [
    "Draw a creature from your imagination.",
    "Sketch a landscape from a dream.",
    "Illustrate a scene from your favorite book.",
]

coding_prompts = [
    "Code a simple game of tic-tac-toe.",
    "Write a program that generates a random password.",
    "Build a web scraper that extracts data from a website.",
]

# Get a random prompt for each category
writing_prompt = random.choice(writing_prompts)
drawing_prompt = random.choice(drawing_prompts)
coding_prompt = random.choice(coding_prompts)

# Display the prompts
st.header(f"Prompt for {today.strftime('%B %d, %Y')}")

st.subheader("Writing Prompt")
st.write(writing_prompt)

st.subheader("Drawing Prompt")
st.write(drawing_prompt)

st.subheader("Coding Prompt")
st.write(coding_prompt)

# Gemini API Key
st.sidebar.title("Gemini API")
api_key = st.sidebar.text_input("Enter your Gemini API key", type="password")

# User input
st.header("Share Your Creation")
user_input = st.text_area("Paste your writing, a description of your drawing, or your code here.")

if st.button("Get Feedback"):
    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(f"Provide feedback on this creative work: {user_input}")
            st.subheader("Gemini's Feedback")
            st.write(response.text)
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.error("Please enter your Gemini API key in the sidebar.")
