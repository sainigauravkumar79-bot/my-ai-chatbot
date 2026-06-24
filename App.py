import streamlit as st
import google.generativeai as genai
from groq import Groq
import openai
import streamlit.components.v1 as components
import time
import urllib.request

# --- Page Configuration ---
st.set_page_config(page_title="JARVIS AI - Assistant Mode 4.5", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")

# --- 🎨 ADVANCED CYBERPUNK & FLOATING WIDGET STYLE SHEET ---
st.markdown("""
<style>
    .stApp { background-color: #030712 !important; color: #00f2fe !important; font-family: 'Courier New', Courier, monospace; }
    
    /* 🔴 FLOATING VOICE CIRCLE BUTTON (SIDEBAR) */
    .voice-trigger-btn {
        background: radial-gradient(circle, #ff007f 0%, #030712 100%);
        border: 2px solid #ff007f; border-radius: 50%; width: 50px; height: 50px;
        box-shadow: 0 0 15px #ff007f; cursor: pointer; display: flex;
        align-items: center; justify-content: center; font-size: 20px;
    }

    /* 🌌 GEMINI LIVE FULL SCREEN INTERFACE (Image 1000092926.jpg Replica) */
    .gemini-live-bg {
        background: radial-gradient(circle at bottom, #0d1b2a 0%, #030712 100%);
        height: 80vh; display: flex; flex-direction: column;
        align-items: center; justify-content: center; border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1); position: relative;
    }
    .gemini-spark {
        font-size: 60px; margin-bottom: 20px;
        background: linear-gradient(45deg, #4285F4, #9B51E0, #EA4335);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .gemini-title {
        color: #ffffff !important; font-family: sans-serif; font-weight: bold;
        font-size: 32px; letter-spacing: -0.5px; text-shadow: none !important; margin-bottom: 50px;
    }
    .bottom-controls {
        position: absolute; bottom: 40px; display: flex; gap: 20px; align-items: center;
    }
    .control-circle {
        background: #1e293b; border: 1px solid rgba(255,255,255,0.2);
        border-radius: 50%; width: 50px; height: 50px; display: flex;
        align-items: center; justify-content: center; color: white; font-size: 20px;
    }
    .main-glow-pill {
        background: linear-gradient(90deg, #1e3a8a, #0284c7);
        border-radius: 30px; width: 140px; height: 55px;
        box-shadow: 0 0 25px rgba(2, 132, 199, 0.6);
    }

    /* 🔵 BLUE-BLACK FLOATING ASSISTANT WIDGET (Image 1000092927.jpg Replica) */
    .floating-assistant-bubble {
        position: fixed;
        bottom: 40%;
        right: 30px;
        width: 70px;
        height: 70px;
        background: radial-gradient(circle, #0f172a 20%, #1e3a8a 80%, #0284c7 100%);
        border: 3px solid #00f2fe;
        border-radius: 50%;
        box-shadow: 0 0 25px rgba(0, 242, 254, 0.8), inset 0 0 15px rgba(0,0,0,0.6);
        z-index: 99999;
        cursor: pointer;
        animation: floatGlow 3s ease-in-out infinite;
    }
    @keyframes floatGlow {
        0% { transform: translateY(0px) scale(1); box-shadow: 0 0 20px rgba(0, 242, 254, 0.6); }
        50% { transform: translateY(-10px) scale(1.05); box-shadow: 0 0 35px rgba(0, 242, 254, 0.9); border-color: #ff007f; }
        100% { transform: translateY(0px) scale(1); box-shadow: 0 0 20px rgba(0, 242, 254, 0.6); }
    }
</style>
""", unsafe_allow_html=True)

# --- States & Core Init ---
if "saved_ai" not in st.session_state: st.session_state.saved_ai = "Groq (Llama 3 - FREE)"
if "saved_key" not in st.session_state: st.session_state.saved_key = ""
if "master_training" not in st.session_state: st.session_state.master_training = ""
if "messages" not in st.session_state: st.session_state.messages = []
if "current_view" not in st.session_state: st.session_state.current_view = "chat"
if "twin_mood" not in st.session_state: st.session_state.twin_mood = "Chill 😎"
if "voice_mode_active" not in st.session_state: st.session_state.voice_mode_active = False
if "floating_widget_active" not in st.session_state: st.session_state.floating_widget_active = False

# --- SIDEBAR TERMINAL ---
with st.sidebar:
    st.markdown("## ⚡ JARVIS CORES")
    if st.button("⬅️ RESET SYSTEM", use_container_width=True):
        st.session_state.voice_mode_active = False
        st.session_state.floating_widget_active = False
        st.session_state.current_view = "setup"; st.rerun()
    
    st.write("---")
    
    # 🔴 SIDE BUTTON FOR GEMINI LIVE VIEW
    st.markdown("### 🎙️ VOICE PROTOCOL")
    if st.button("🔴 OPEN VOICE INTERFACE", use_container_width=True):
        st.session_state.voice_mode_active = True; st.rerun()

    st.write("---")
    
    # 🔵 ASSISTANT WIDGET TOGGLE (IMAGE 1000092927.jpg CORE)
    st.markdown("### 📱 SYSTEM OVERLAY")
    widget_toggle = st.toggle("🔓 ACTIVATE FLOATING ASSISTANT", value=st.session_state.floating_widget_active)
    if widget_toggle != st.session_state.floating_widget_active:
        st.session_state.floating_widget_active = widget_toggle
        st.rerun()
    st.write("Enables the floating blue-black assistant bubble on the interface grid.")

# --- VIEW 1: SETUP ---
if st.session_state.current_view == "setup":
    st.title("🧠 MIRROR AI: Core Setup")
    ai_choice = st.selectbox("Neural Engine:", ("Groq (Llama 3 - FREE)", "Google Gemini"))
    key_input = st.text_input("API Key:", type="password", value=st.session_state.saved_key)
    master_input = st.text_area("Training Context:", value=st.session_state.master_training)
    if st.button("ACTIVATE CORES"):
        st.session_state.saved_ai = ai_choice; st.session_state.saved_key = key_input; st.session_state.master_training = master_input
        st.session_state.current_view = "chat"; st.rerun()

# --- VIEW 2: CHAT ROOM / VOICE INTERFACE ---
elif st.session_state.current_view == "chat":
    
    # 🔵 अगर फ्लोटिंग असिस्टेंट एक्टिव है, तो स्क्रीन पर बबल रेंडर करो (Image 1000092927.jpg)
    if st.session_state.floating_widget_active and not st.session_state.voice_mode_active:
        # Streamlit में क्लिक डिटेक्ट करने के लिए हम एक हिडन बटन के ऊपर HTML बबल प्लेस कर रहे हैं
        if st.button("", key="hidden_bubble_trigger", help="Click to Wake Jarvis Live"):
            st.session_state.voice_mode_active = True
            st.rerun()
        
        # विज़ुअल ग्लोइंग ओवरले डिज़ाइन
        st.markdown('<div class="floating-assistant-bubble"></div>', unsafe_allow_html=True)
    
    # 🌌 IF VOICE MODE IS ACTIVE -> SHOW IMAGE 1000092926.jpg REPLICA UI
    if st.session_state.voice_mode_active:
        st.markdown("""
        <div class="gemini-live-bg">
            <div class="gemini-spark">✦</div>
            <div class="gemini-title">Ready when you are</div>
            
            <div class="bottom-controls">
                <div class="control-circle">📷</div>
                <div class="control-circle">📤</div>
                <div class="main-glow-pill"></div>
                <div class="control-circle">🎙️</div>
                <div class="control-circle" style="color:#ef4444;">✕</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        audio_command = st.audio_input("Speak to Jarvis Layer:")
        if audio_command:
            st.toast("Capturing voice frequencies...", icon="🎙️")
            
        if st.button("📴 CLOSE ASSISTANT PROTOCOL", use_container_width=True):
            st.session_state.voice_mode_active = False; st.rerun()
            
    # 💬 TRADITIONAL CHAT MODE UI
    else:
        st.title("🧠 Jarvis Main Command Room")
        st.write("---")
        st.write("💡 *Tip: Turn on 'Activate Floating Assistant' in the sidebar to view the overlay widget.*")
        st.write("---")
        
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f'<div class="user-msg-container"><div class="user-msg">🧑 <b>You:</b><br>{message["content"]}</div></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="twin-msg-container"><div class="twin-msg">🧠 <b>Mirror Twin:</b><br>{message["content"]}</div></div>', unsafe_allow_html=True)

        chat_input_val = st.chat_input("Input system instructions...")
        if chat_input_val:
            st.session_state.messages.append({"role": "user", "content": chat_input_val})
            st.session_state.messages.append({"role": "assistant", "content": f"Acknowledged. Action logged under active node parameters."})
            st.rerun()
            
