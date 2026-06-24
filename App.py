import streamlit as st
import google.generativeai as genai
from groq import Groq
import openai
import streamlit.components.v1 as components
import time
import urllib.request
import json

# --- Page Configuration ---
st.set_page_config(page_title="JARVIS AI - Real Voice Core 4.8", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")

# --- 🎨 DARK CYBERPUNK & FLOATING WIDGET STYLE SHEET ---
st.markdown("""
<style>
    .stApp { background-color: #030712 !important; color: #00f2fe !important; font-family: 'Courier New', Courier, monospace; }
    .user-msg-container { display: flex; justify-content: flex-end; margin-bottom: 15px; width: 100%; }
    .user-msg { 
        background: linear-gradient(135deg, #0052d4, #4364f7, #6fb1fc); 
        color: white; padding: 15px 20px; border-radius: 25px 25px 4px 25px; 
        max-width: 80%; font-family: sans-serif; box-shadow: 0px 0px 15px rgba(67, 100, 247, 0.6); border: 1px solid #00f2fe;
    }
    .twin-msg-container { display: flex; flex-direction: column; align-items: flex-start; margin-bottom: 15px; width: 100%; }
    .twin-msg { 
        background: #0d1117; color: #00f2fe; padding: 15px 20px; border-radius: 25px 25px 25px 4px; 
        max-width: 80%; font-family: sans-serif; border: 1px solid #ff007f; box-shadow: 0px 0px 15px rgba(255, 0, 127, 0.4);
    }
    h1, h2, h3 { color: #00f2fe !important; text-shadow: 0 0 10px #00f2fe, 0 0 20px #0052d4; }
    
    .summary-pin-card {
        background: linear-gradient(90deg, #1e1b4b, #0f172a);
        border-left: 5px solid #ff007f; padding: 15px; border-radius: 8px;
        margin-bottom: 20px;
    }

    /* 🌌 GEMINI LIVE REPLICA UI (Image 1000092926.jpg) */
    .gemini-live-bg {
        background: radial-gradient(circle at bottom, #0d1b2a 0%, #030712 100%);
        height: 70vh; display: flex; flex-direction: column;
        align-items: center; justify-content: center; border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1); position: relative;
    }
    .gemini-spark { 
        font-size: 70px; margin-bottom: 25px; 
        background: linear-gradient(45deg, #4285F4, #9B51E0, #EA4335);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .gemini-title { color: #ffffff !important; font-family: sans-serif; font-weight: bold; font-size: 32px; margin-bottom: 50px; }
    
    /* 🔵 BLUE-BLACK FLOATING BUBBLE (Image 1000092927.jpg) */
    .floating-assistant-bubble {
        position: fixed; bottom: 40%; right: 30px; width: 70px; height: 70px;
        background: radial-gradient(circle, #0f172a 20%, #1e3a8a 80%, #0284c7 100%);
        border: 3px solid #00f2fe; border-radius: 50%;
        box-shadow: 0 0 25px rgba(0, 242, 254, 0.8); z-index: 99999; cursor: pointer;
        animation: floatGlow 3s ease-in-out infinite;
    }
    @keyframes floatGlow {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); border-color: #ff007f; }
        100% { transform: translateY(0px); }
    }
</style>
""", unsafe_allow_html=True)

# --- 📅 MEMORY CORES & STATES ---
if "saved_ai" not in st.session_state: st.session_state.saved_ai = "Groq (Llama 3 - FREE)"
if "saved_key" not in st.session_state: st.session_state.saved_key = ""
if "master_training" not in st.session_state: st.session_state.master_training = ""
if "messages" not in st.session_state: st.session_state.messages = []
if "current_view" not in st.session_state: st.session_state.current_view = "setup"
if "twin_mood" not in st.session_state: st.session_state.twin_mood = "Chill 😎"
if "user_sentiment" not in st.session_state: st.session_state.user_sentiment = "Neutral 🧘"
if "pinned_summary" not in st.session_state: st.session_state.pinned_summary = "चैट अभी शुरू हुई है।"
if "project_milestones" not in st.session_state: st.session_state.project_milestones = {}
if "voice_mode_active" not in st.session_state: st.session_state.voice_mode_active = False
if "floating_widget_active" not in st.session_state: st.session_state.floating_widget_active = False

# --- LIVE WEB SEARCH HELPER ---
def live_web_search(query):
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=5) as response:
            html = response.read().decode('utf-8')
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            results = [a.get_text().strip() for a in soup.find_all('a', class_='result__snippet')[:3]]
            return "\n".join(results) if results else "No data."
    except Exception:
        return "Offline."

# --- AI RESPONSE ROUTER ---
def process_ai_response(user_message):
    current_ai = st.session_state.saved_ai
    current_key = st.session_state.saved_key
    if not current_key:
        return "⚠️ Please add your API key in Setup first!"
        
    master_prompt = f"You are Gaurav's advanced digital twin. Context: {st.session_state.master_training}. Mood: {st.session_state.twin_mood}. Respond logically and concisely. End strictly by appending [SENTIMENT: word] and [SUMMARY: sentence]. User: {user_message}"
    try:
        if current_ai == "Google Gemini":
            genai.configure(api_key=current_key)
            bot_reply = genai.GenerativeModel('gemini-2.5-flash').generate_content(master_prompt).text
        elif current_ai == "Groq (Llama 3 - FREE)":
            bot_reply = Groq(api_key=current_key).chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": master_prompt}]).choices[0].message.content
        elif current_ai == "OpenAI (ChatGPT)":
            bot_reply = openai.OpenAI(api_key=current_key).chat.completions.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": master_prompt}]).choices[0].message.content
        
        if "[SENTIMENT:" in bot_reply:
            st.session_state.user_sentiment = bot_reply.split("[SENTIMENT:")[1].split("]")[0].strip()
            bot_reply = bot_reply.split("[SENTIMENT:")[0]
        if "[SUMMARY:" in bot_reply:
            st.session_state.pinned_summary = bot_reply.split("[SUMMARY:")[1].split("]")[0].strip()
            bot_reply = bot_reply.split("[SUMMARY:")[0]
            
        return bot_reply
    except Exception as e:
        return f"Neural Error: {e}"

# --- 💻 SIDEBAR TERMINAL ---
if st.session_state.current_view != "setup":
    with st.sidebar:
        st.markdown("## ⚡ JARVIS CORES")
        if st.button("⬅️ RESET SYSTEM", use_container_width=True):
            st.query_params.clear(); st.session_state.current_view = "setup"; st.rerun()
        st.write("---")
        if st.button("🔴 OPEN VOICE ASSISTANT", use_container_width=True):
            st.session_state.voice_mode_active = True; st.rerun()
        widget_toggle = st.toggle("🔓 FLOATING ASSISTANT WIDGET", value=st.session_state.floating_widget_active)
        if widget_toggle != st.session_state.floating_widget_active:
            st.session_state.floating_widget_active = widget_toggle; st.rerun()
        st.write("---")
        st.session_state.twin_mood = st.select_slider("Mood:", options=["Angry 😡", "Professional 💼", "Chill 😎", "Funny 🤪"], value=st.session_state.twin_mood)

# --- VIEW 1: SETUP PAGE ---
if st.session_state.current_view == "setup":
    st.title("🧠 MIRROR AI: Core Setup")
    ai_choice = st.selectbox("Select Neural Engine:", ("Groq (Llama 3 - FREE)", "Google Gemini", "OpenAI (ChatGPT)"))
    key_input = st.text_input("Enter API Key:", type="password", value=st.session_state.saved_key)
    master_input = st.text_area("Train Your Twin:", value=st.session_state.master_training, height=150)
    if st.button("🔥 ACTIVATE DIGITAL TWIN", use_container_width=True):
        if not key_input or not master_input: st.error("⚠️ API Key & Training Context required!")
        else:
            st.session_state.saved_ai = ai_choice; st.session_state.saved_key = key_input; st.session_state.master_training = master_input
            st.session_state.current_view = "chat"; st.query_params["page"] = "chat"; st.rerun()

# --- VIEW 2: COMMAND ROOM & LIVE VOICE INTERFACE ---
elif st.session_state.current_view == "chat":
    
    # 🔵 FLOATING ASSISTANT OVERLAY
    if st.session_state.floating_widget_active and not st.session_state.voice_mode_active:
        if st.button("", key="hidden_bubble_trigger"):
            st.session_state.voice_mode_active = True; st.rerun()
        st.markdown('<div class="floating-assistant-bubble"></div>', unsafe_allow_html=True)
        
    # 🌌 IMAGE 1000092926.jpg REPLICA WITH REAL JAVASCRIPT LISTENING CORE
    if st.session_state.voice_mode_active:
        st.markdown("""
        <div class="gemini-live-bg">
            <div class="gemini-spark">✦</div>
            <div class="gemini-title">Ready when you are</div>
            <p style='color:#00f2fe; font-family:sans-serif; font-size:14px; margin-top:-30px;'>🎤 Speak clearly. Your twin is listening via web matrix core.</p>
        </div>
        """, unsafe_allow_html=True)

        # 🚀 REAL MIC LISTENING LAYER FOR STREAMLIT
        voice_input = st.audio_input("Tap Microphone icon below to speak:")
        
        # टेक्स्ट बैकअप फॉलबैक ताकि वॉयस काम न करने पर भी टाइप किया जा सके
        voice_fallback = st.text_input("Or type voice instruction manually here:")
        
        if voice_fallback:
            reply = process_ai_response(voice_fallback)
            st.session_state.messages.append({"role": "user", "content": voice_fallback})
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.session_state.voice_mode_active = False; st.rerun()

        if st.button("📴 CLOSE ASSISTANT PROTOCOL", use_container_width=True):
            st.session_state.voice_mode_active = False; st.rerun()
            
    # 💬 TRADITIONAL CHAT MODE UI
    else:
        st.title("🧠 Jarvis Main Command Room")
        st.markdown(f"""
        <div class="summary-pin-card">
            <span style='color:#ff007f; font-weight:bold;'>📌 LIVE MATRIX PIN:</span> <span style='color:#ffffff;'>{st.session_state.pinned_summary}</span>
        </div>
        """, unsafe_allow_html=True)
        
        col_m, col_s, col_l = st.columns(3)
        with col_m: st.markdown(f"**Mood:** `{st.session_state.twin_mood}`")
        with col_s: st.markdown(f"**Vibe:** `{st.session_state.user_sentiment}`")
        with col_l: live_search_on = st.toggle("🌐 LIVE WEB SEARCH", value=False)
        st.write("---")

        # History Render
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f'<div class="user-msg-container"><div class="user-msg">🧑 <b>You:</b><br>{message["content"]}</div></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="twin-msg-container"><div class="twin-msg">🧠 <b>Mirror Twin:</b><br>{message["content"]}</div></div>', unsafe_allow_html=True)

        st.write("---")
        chat_box_input = st.chat_input("Input system commands here...")
        
        if chat_box_input:
            st.session_state.messages.append({"role": "user", "content": chat_box_input})
            reply = process_ai_response(chat_box_input)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.rerun()
        
