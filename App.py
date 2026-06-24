import streamlit as st
import google.generativeai as genai
from groq import Groq
import openai
import streamlit.components.v1 as components
import urllib.parse
import urllib.request

# --- Page Configuration ---
st.set_page_config(page_title="JARVIS AI - Speech Core 5.0", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")

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
    h1, h2, h3 { color: #00f2fe !important; text-shadow: 0 0 10px #00f2fe; }
    .summary-pin-card { background: linear-gradient(90deg, #1e1b4b, #0f172a); border-left: 5px solid #ff007f; padding: 15px; border-radius: 8px; margin-bottom: 20px; }

    /* 🌌 GEMINI LIVE REPLICA UI */
    .gemini-live-bg {
        background: radial-gradient(circle at bottom, #0d1b2a 0%, #030712 100%);
        height: 50vh; display: flex; flex-direction: column;
        align-items: center; justify-content: center; border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1); position: relative; margin-bottom: 20px;
    }
    .gemini-spark { font-size: 70px; margin-bottom: 15px; color: #4285F4; animation: pulse 2s infinite; }
    .gemini-title { color: #ffffff !important; font-family: sans-serif; font-weight: bold; font-size: 32px; }
    
    /* 🔵 BLUE-BLACK FLOATING BUBBLE */
    .floating-assistant-bubble {
        position: fixed; bottom: 40%; right: 30px; width: 70px; height: 70px;
        background: radial-gradient(circle, #0f172a 20%, #1e3a8a 80%, #0284c7 100%);
        border: 3px solid #00f2fe; border-radius: 50%;
        box-shadow: 0 0 25px rgba(0, 242, 254, 0.8); z-index: 99999; cursor: pointer;
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
if "voice_mode_active" not in st.session_state: st.session_state.voice_mode_active = False
if "floating_widget_active" not in st.session_state: st.session_state.floating_widget_active = False

# --- AI RESPONSE ROUTER ---
def process_ai_response(user_message):
    current_ai = st.session_state.saved_ai
    current_key = st.session_state.saved_key
    if not current_key:
        return "⚠️ Please add your API key in Setup page!"
        
    master_prompt = f"You are Gaurav's digital twin. Context: {st.session_state.master_training}. Mood: {st.session_state.twin_mood}. Respond logically and naturally. End strictly by appending [SENTIMENT: word] and [SUMMARY: sentence]. User: {user_message}"
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

# --- SIDEBAR TERMINAL ---
if st.session_state.current_view != "setup":
    with st.sidebar:
        st.markdown("## ⚡ JARVIS CORES")
        if st.button("⬅️ RESET SYSTEM", use_container_width=True):
            st.query_params.clear(); st.session_state.current_view = "setup"; st.rerun()
        st.write("---")
        if st.button("🔴 OPEN VOICE ASSISTANT", use_container_width=True):
            st.session_state.voice_mode_active = True; st.rerun()
        st.session_state.floating_widget_active = st.toggle("🔓 FLOATING ASSISTANT WIDGET", value=st.session_state.floating_widget_active)
        st.write("---")
        st.session_state.twin_mood = st.select_slider("Mood:", options=["Angry 😡", "Professional 💼", "Chill 😎", "Funny 🤪"], value=st.session_state.twin_mood)

# --- VIEW 1: SETUP PAGE ---
if st.session_state.current_view == "setup":
    st.title("🧠 MIRROR AI: Core Setup")
    ai_choice = st.selectbox("Select AI Neural Engine:", ("Groq (Llama 3 - FREE)", "Google Gemini", "OpenAI (ChatGPT)"))
    key_input = st.text_input("Enter API Key:", type="password", value=st.session_state.saved_key)
    master_input = st.text_area("Train Your Twin:", value=st.session_state.master_training, height=150)
    if st.button("🔥 ACTIVATE DIGITAL TWIN", use_container_width=True):
        if not key_input or not master_input: st.error("⚠️ API Key & Context required!")
        else:
            st.session_state.saved_ai = ai_choice; st.session_state.saved_key = key_input; st.session_state.master_training = master_input
            st.session_state.current_view = "chat"; st.rerun()

# --- VIEW 2: MAIN WORKSPACE ---
elif st.session_state.current_view == "chat":
    
    # 🔵 RENDER FLOATING ASSISTANT OVERLAY
    if st.session_state.floating_widget_active and not st.session_state.voice_mode_active:
        if st.button("", key="hidden_bubble_trigger"):
            st.session_state.voice_mode_active = True; st.rerun()
        st.markdown('<div class="floating-assistant-bubble"></div>', unsafe_allow_html=True)
        
    # 🌌 VOICE ASSISTANT ACTIVE INTERFACE
    if st.session_state.voice_mode_active:
        st.markdown("""
        <div class="gemini-live-bg">
            <div class="gemini-spark">✦</div>
            <div class="gemini-title">Ready when you are</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 🎤 Web JavaScript Voice Engine Active")
        
        # 🌐 JAVASCRIPT DIRECT VOICE CAPTURE ENGINE
        voice_component = """
        <div style="background:#0f172a; border: 1px solid #00f2fe; padding:15px; border-radius:10px; text-align:center;">
            <button id="start-record-btn" style="background:#ff007f; color:white; border:none; padding:12px 25px; border-radius:20px; font-weight:bold; cursor:pointer;">🗣️ TAP TO SPEAK (LIVE MIC)</button>
            <p id="status-text" style="color:#00f2fe; font-family:sans-serif; font-size:14px; margin-top:10px;">Status: Microphone Idle</p>
        </div>

        <script>
            const startBtn = document.getElementById('start-record-btn');
            const statusText = document.getElementById('status-text');

            if ('webkitSpeechRecognition' in window || 'speechRecognition' in window) {
                const SpeechRecognition = window.webkitSpeechRecognition || window.speechRecognition;
                const recognition = new SpeechRecognition();
                
                recognition.continuous = false;
                recognition.lang = 'hi-IN'; // Supports both Hindi and English
                recognition.interimResults = false;

                startBtn.addEventListener('click', () => {
                    recognition.start();
                    statusText.innerText = "Status: Listening... Speak Now!";
                    startBtn.style.background = "#22c55e";
                });

                recognition.onresult = (event) => {
                    const speechToText = event.results[0][0].transcript;
                    statusText.innerText = "Captured: " + speechToText;
                    startBtn.style.background = "#ff007f";
                    
                    // Sending captured text to Streamlit backend instantly via query params or clipboard fallback
                    const url = new URL(window.parent.location.href);
                    url.searchParams.set('voice_input', speechToText);
                    window.parent.location.href = url.href;
                };

                recognition.onerror = (e) => {
                    statusText.innerText = "Mic Error or Permission Blocked.";
                    startBtn.style.background = "#ef4444";
                };
            } else {
                statusText.innerText = "Web Speech API not supported in this browser.";
            }
        </script>
        """
        components.html(voice_component, height=120)

        # Catch Voice Data from JavaScript
        query_args = st.query_params
        if "voice_input" in query_args:
            captured_text = query_args["voice_input"]
            st.query_params.clear() # Clear param to avoid loops
            
            st.session_state.messages.append({"role": "user", "content": captured_text})
            reply = process_ai_response(captured_text)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.session_state.voice_mode_active = False; st.rerun()

        if st.button("📴 CLOSE ASSISTANT PROTOCOL", use_container_width=True):
            st.session_state.voice_mode_active = False; st.rerun()
            
    # 💬 TRADITIONAL CHAT MODE UI
    else:
        st.title("🧠 Jarvis Main Command Room")
        st.markdown(f'<div class="summary-pin-card"><b>📌 SYSTEM SUMMARY PIN:</b> {st.session_state.pinned_summary}</div>', unsafe_allow_html=True)
        
        # Render History
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f'<div class="user-msg-container"><div class="user-msg">🧑 <b>You:</b><br>{message["content"]}</div></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="twin-msg-container"><div class="twin-msg">🧠 <b>Mirror Twin:</b><br>{message["content"]}</div></div>', unsafe_allow_html=True)

        chat_box_input = st.chat_input("Input system commands here...")
        if chat_box_input:
            st.session_state.messages.append({"role": "user", "content": chat_box_input})
            reply = process_ai_response(chat_box_input)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.rerun()
        
