import streamlit as st
import openai
import google.generativeai as genai
from groq import Groq

st.set_page_config(page_title="Gaurav's Multi-AI Chatbot", page_icon="🤖")
st.title("🤖 Gaurav's Multi-AI Chatbot")
st.write("अपनी पसंद का AI चुनिए, API Key डालिए और चैट करिए!")

# 1. AI प्लेटफॉर्म चुनने का ड्रॉपडाउन
ai_option = st.selectbox(
    "कौन सा AI इस्तेमाल करना चाहते हैं?",
    ("Google Gemini", "Groq (Llama 3 - FREE)", "OpenAI (ChatGPT)")
)

# 2. USER से API Key लेना
user_api_key = st.text_input(f"अपनी {ai_option} API Key यहाँ पेस्ट करें:", type="password")

# चैट हिस्ट्री सेट करना
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 3. चैट इनपुट बॉक्स
if user_message := st.chat_input("यहाँ अपना सवाल लिखें..."):
    if not user_api_key:
        st.error(f"कृपया पहले ऊपर अपनी {ai_option} API Key डालें!")
    else:
        st.chat_message("user").markdown(user_message)
        st.session_state.messages.append({"role": "user", "content": user_message})

        try:
            bot_reply = ""
            
            # --- GOOGLE GEMINI ---
            if ai_option == "Google Gemini":
                genai.configure(api_key=user_api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                response = model.generate_content(user_message)
                bot_reply = response.text
            
            # --- GROQ (FREE LLAMA) ---
            elif ai_option == "Groq (Llama 3 - FREE)":
                client = Groq(api_key=user_api_key)
                completion = client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[{"role": "user", "content": user_message}]
                )
                bot_reply = completion.choices[0].message.content
            
            # --- OPENAI ---
            elif ai_option == "OpenAI (ChatGPT)":
                client = openai.OpenAI(api_key=user_api_key)
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": user_message}]
                )
                bot_reply = response.choices[0].message.content

            # जवाब स्क्रीन पर दिखाना और सेव करना
            with st.chat_message("assistant"):
                st.markdown(bot_reply)
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            
        except Exception as e:
            st.error(f"एरर आया! कृपया चेक करें कि की (Key) सही है या नहीं। एरर: {e}")
            
