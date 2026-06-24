import streamlit as st
import google.generativeai as genai
from groq import Groq
import openai
import streamlit.components.v1 as components
import time
import urllib.request
import json

# --- Page Configuration ---
st.set_page_config(page_title="JARVIS AI - Brain Connected 4.6", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")

# --- 🎨 ADVANCED CYBERPUNK STYLE SHEET ---
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
    
    .diagnostic-box {
        background: #090d16; border: 1px solid #22c55e;
        padding: 10px; border-radius: 8px; font-size: 11px; color: #22c55e;
    }
    .summary-pin-card {
        background: linear-gradient(90deg, #1e1b4b, #0f172a);
        border-left: 5px solid #ff007f; padding: 15px; border-radius: 8px;
        margin-bottom: 20px;
    }

    /* 🌌 GEMINI LIVE REPLICA UI */
    .gemini-live-bg {
        background: radial-gradient(circle at bottom, #0d1b2a 0%, #030712 100%);
        height: 80vh; display: flex; flex-direction: column;
        align-items: center; justify-content: center; border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1); position: relative;
    }
    .gemini-spark { font-size: 60px; margin-bottom: 20px; color: #4285F4; }
    .gemini-title { color: #ffffff !important; font-family: sans-serif; font-weight: bold; font-size: 32px; margin-bottom: 50px; }
    .bottom-controls { position: absolute; bottom: 40px; display: flex; gap: 20px; align-items: center; }
    .control-circle { background: #1e293b; border: 1px solid rgba(255,255,255,0.2); border-radius: 50%; width: 50px; height: 50px; display: flex; align-items: center; justify-content: center; color: white; font-size: 20px; }
    .main-glow-pill { background: linear-gradient(90deg, #1e3a8a, #0284c7); border-radius: 30px; width: 140px; height: 55px; box-shadow: 0 0 25px rgba(2, 132, 199, 0.6); }

    /* 🔵 BLUE-BLACK FLOATING BUBBLE */
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
if "code_snippets" not in st.session_state: st.session_state.code_snippets = {}
if "voice_mode_active" not in st.session_state: st.session_state.voice_mode_active = False
if "floating_widget_active" not in st.session_state: st.session_state.floating_widget_active = False

# URL Tracking Check
query_params = st.query_params
if "page" not in query_params:
    st.session_state.current_view = "setup"
elif query_params["page"] == "chat" and st.session_state.current_view == "setup":
    st.session_state.current_view = "chat"

# --- 🌐 SMART INTERNET LIVE SEARCH HELPER ---
def live_web_search(query):
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=5) as response:
            html = response.read().decode('utf-8')
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            results = []
            for a in soup.find_all('a', class_='result__snippet')[:3]:
                results.append(a.get_text().strip())
            return "\n".join(results) if results else "No direct web data."
    except Exception:
        return "Web Grid Connection Offline."

# --- 💻 SIDEBAR TERMINAL ---
if st.session_state.current_view != "setup":
    with st.sidebar:
        st.markdown("## ⚡ JARVIS TERMINAL")
        if st.button("⬅️ SYSTEM RESET", use_container_width=True):
            st.query_params.clear(); st.session_state.current_view = "setup"; st.rerun()
            
        st.write("---")
        st.markdown("### 🎙️ ASSISTANT TRIGGER")
        if st.button("🔴 OPEN VOICE INTERFACE", use_container_width=True):
            st.session_state.voice_mode_active = True; st.rerun()
            
        widget_toggle = st.toggle("🔓 ACTIVATE FLOATING ASSISTANT", value=st.session_state.floating_widget_active)
        if widget_toggle != st.session_state.floating_widget_active:
            st.session_state.floating_widget_active = widget_toggle; st.rerun()

        st.write("---")
        st.markdown("### 📊 PROJECT TRACKER")
        with st.expander("🛠️ Manage Milestones", expanded=False):
            p_name = st.text_input("Project Name:")
            t_total = st.number_input("Total Tasks:", min_value=1, value=5)
            t_done = st.number_input("Completed Tasks:", min_value=0, value=0)
            if st.button("💾 Save Project Board"):
                if p_name: st.session_state.project_milestones[p_name] = {"total": t_total, "done": min(t_done, t_total)}
        
        if st.session_state.project_milestones:
            for p, data in list(st.session_state.project_milestones.items()):
                st.markdown(f"**{p}** ({data['done']}/{data['total']})")
                st.progress(data["done"] / data["total"])

        st.write("---")
        st.markdown("### 🎭 TWIN EMOTION")
        st.session_state.twin_mood = st.select_slider("Select Mood:", options=["Angry 😡", "Professional 💼", "Chill 😎", "Funny 🤪"], value=st.session_state.twin_mood)

# --- VIEW 1: SETUP PAGE ---
if st.session_state.current_view == "setup":
    st.title("🧠 MIRROR AI: Cyberpunk Core Setup")
    st.write("---")
    ai_choice = st.selectbox("Select AI Neural Engine:", ("Groq (Llama 3 - FREE)", "Google Gemini", "OpenAI (ChatGPT)"))
    key_input = st.text_input(f"Enter {ai_choice} API Key:", type="password", value=st.session_state.saved_key)
    master_input = st.text_area("Train Your Twin (Write about yourself):", placeholder="जैसे: मेरा नाम गौरव है...", value=st.session_state.master_training, height=150)
    
    if st.button("🔥 ACTIVATE DIGITAL TWIN 🚀", use_container_width=True):
        if not key_input or not master_input: st.error("⚠️ API Key और ट्रेनिंग डेटा अनिवार्य हैं!")
        else:
            st.session_state.saved_ai = ai_choice; st.session_state.saved_key = key_input; st.session_state.master_training = master_input
            st.session_state.current_view = "chat"; st.query_params["page"] = "chat"; st.rerun()

# --- VIEW 2: CHAT ROOM & VOICE INTELLIGENCE ---
elif st.session_state.current_view == "chat":
    
    # 🔵 RENDER FLOATING ASSISTANT IF ACTIVE
    if st.session_state.floating_widget_active and not st.session_state.voice_mode_active:
        if st.button("", key="hidden_bubble_trigger"):
            st.session_state.voice_mode_active = True; st.rerun()
        st.markdown('<div class="floating-assistant-bubble"></div>', unsafe_allow_html=True)
        
    # 🌌 IF VOICE MODE IS ACTIVE (Gemini Live UI)
    if st.session_state.voice_mode_active:
        st.markdown("""
        <div class="gemini-live-bg">
            <div class="gemini-spark">✦</div>
            <div class="gemini-title">Ready when you are</div>
            <div class="bottom-controls">
                <div class="control-circle">📷</div><div class="control-circle">📤</div>
                <div class="main-glow-pill"></div>
                <div class="control-circle">🎙️</div><div class="control-circle" style="color:#ef4444;">✕</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        audio_command = st.audio_input("Speak to Jarvis Protocol Layer:")
        if audio_command: st.toast("Capturing voice stream matrix...", icon="🎙️")
        if st.button("📴 EXIT VOICE MODE", use_container_width=True):
            st.session_state.voice_mode_active = False; st.rerun()
            
    # 💬 TRADITIONAL CHAT MODE (FULLY BACKEND CONNECTED NOW!)
    else:
        st.title("🧠 Jarvis Main Command Room")
        st.markdown(f"""
        <div class="summary-pin-card">
            <span style='color:#ff007f; font-weight:bold;'>📌 LIVE MATRIX PIN:</span> 
            <span style='color:#ffffff;'>{st.session_state.pinned_summary}</span>
        </div>
        """, unsafe_allow_html=True)
        
        col_m, col_s, col_l = st.columns(3)
        with col_m: st.markdown(f"**Mood:** `{st.session_state.twin_mood}`")
        with col_s: st.markdown(f"**User Sentiment:** `{st.session_state.user_sentiment}`")
        with col_l: live_search_on = st.toggle("🌐 LIVE WEB SEARCH", value=False)
        st.write("---")

        # Mummy Call Interaction Protocol Render
        if st.session_state.messages and "mummy ko call lagao" in st.session_state.messages[-1]["content"].lower():
            st.markdown(f"""
            <div style="background: #021a0f; border: 2px solid #22c55e; border-radius:12px; padding:20px; margin-bottom:15px;">
                <b style="color:#22c55e;">📡 MUMMY CALL INTERFACE ACTIVATED</b><br>
                Synced Profile: <code>Gaurav_Voice_v3.2.bin</code> | Vibe: {st.session_state.user_sentiment}
            </div>
            """, unsafe_allow_html=True)

        # Render History
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f'<div class="user-msg-container"><div class="user-msg">🧑 <b>You:</b><br>{message["content"]}</div></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="twin-msg-container"><div class="twin-msg">🧠 <b>Mirror Twin:</b><br>{message["content"]}</div></div>', unsafe_allow_html=True)

        st.write("---")
        chat_box_input = st.chat_input("Input system commands here...")
        
        if chat_box_input:
            user_message = chat_box_input
            st.session_state.messages.append({"role": "user", "content": user_message})

            web_context = live_web_search(user_message) if live_search_on else ""
            bot_reply = ""
            current_ai = st.session_state.saved_ai
            current_key = st.session_state.saved_key
            
            # 🧠 REAL AI BRAIN ENGINE PIPELINE CONNECTED BACK!
            if current_key:
                master_prompt = f"You are Gaurav's advanced digital twin. Training Context: {st.session_state.master_training}. Mood State: {st.session_state.twin_mood}. Web Context: {web_context}. Chat logically. End your response by strictly appending [SENTIMENT: current mood word] and [SUMMARY: short conversation summary line]. User said: {user_message}"
                try:
                    if current_ai == "Google Gemini":
                        genai.configure(api_key=current_key)
                        bot_reply = genai.GenerativeModel('gemini-2.5-flash').generate_content(master_prompt).text
                    elif current_ai == "Groq (Llama 3 - FREE)":
                        bot_reply = Groq(api_key=current_key).chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": master_prompt}]).choices[0].message.content
                    elif current_ai == "OpenAI (ChatGPT)":
                        bot_reply = openai.OpenAI(api_key=current_key).chat.completions.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": master_prompt}]).choices[0].message.content
                except Exception as e:
                    bot_reply = f"System Grid Error: {e}"

                if bot_reply:
                    # Parse Sentiment and Summary tags
                    if "[SENTIMENT:" in bot_reply:
                        st.session_state.user_sentiment = bot_reply.split("[SENTIMENT:")[1].split("]")[0].strip()
                        bot_reply = bot_reply.split("[SENTIMENT:")[0]
                    if "[SUMMARY:" in bot_reply:
                        st.session_state.pinned_summary = bot_reply.split("[SUMMARY:")[1].split("]")[0].strip()
                        bot_reply = bot_reply.split("[SUMMARY:")[0]

                    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                    st.rerun()
            else:
                st.warning("⚠️ कृपया सेटअप पेज पर जाकर API Key दर्ज करें ताकि जार्विस का दिमाग काम कर सके!")
        
