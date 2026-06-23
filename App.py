import streamlit as st
import google.generativeai as genai
from groq import Groq
import openai
import streamlit.components.v1 as components
import time

# --- पूरे पेज पर चैट फैलाने के लिए Config ---
st.set_page_config(page_title="JARVIS AI - Cyber Twin", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")

# --- FEATURE 4: 🎨 DARK CYBERPUNK JARVIS UI ---
st.markdown("""
<style>
    /* पूरे ऐप का बैकग्राउंड और टेक्स्ट कलर */
    .stApp {
        background-color: #030712 !important;
        color: #00f2fe !important;
        font-family: 'Courier New', Courier, monospace;
    }
    
    /* साइबरपंक चैट बबल्स */
    .user-msg-container { display: flex; justify-content: flex-end; margin-bottom: 15px; width: 100%; }
    .user-msg { 
        background: linear-gradient(135deg, #0052d4, #4364f7, #6fb1fc); 
        color: white; padding: 15px 20px; border-radius: 25px 25px 4px 25px; 
        max-width: 80%; font-family: sans-serif;
        box-shadow: 0px 0px 15px rgba(67, 100, 247, 0.6);
        border: 1px solid #00f2fe;
    }
    .twin-msg-container { display: flex; flex-direction: column; align-items: flex-start; margin-bottom: 15px; width: 100%; }
    .twin-msg { 
        background: #0d1117; 
        color: #00f2fe; padding: 15px 20px; border-radius: 25px 25px 25px 4px; 
        max-width: 80%; font-family: sans-serif;
        border: 1px solid #ff007f; 
        box-shadow: 0px 0px 15px rgba(255, 0, 127, 0.4);
    }
    
    /* ग्लोइंग हेडिंग्स */
    h1, h2, h3 {
        color: #00f2fe !important;
        text-shadow: 0 0 10px #00f2fe, 0 0 20px #0052d4;
    }
    
    /* सिमुलेटर कार्ड्स */
    .simulator-card {
        background: #111827;
        border: 2px dashed #ff007f;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin: 15px 0;
        box-shadow: 0 0 20px rgba(255, 0, 127, 0.5);
        animation: pulse 1.5s infinite alternate;
    }
    @keyframes pulse {
        from { transform: scale(1); }
        to { transform: scale(1.02); }
    }
</style>
""", unsafe_allow_html=True)

# --- FEATURE 1: 📅 JARVIS DYNAMIC MEMORY (SESSION STATE CORES) ---
if "saved_ai" not in st.session_state: st.session_state.saved_ai = "Groq (Llama 3 - FREE)"
if "saved_key" not in st.session_state: st.session_state.saved_key = ""
if "master_training" not in st.session_state: st.session_state.master_training = ""
if "voice_training" not in st.session_state: st.session_state.voice_training = ""
if "messages" not in st.session_state: st.session_state.messages = []
if "current_view" not in st.session_state: st.session_state.current_view = "setup"
if "jarvis_mode" not in st.session_state: st.session_state.jarvis_mode = "Off"
# FEATURE 2: Mood Selector Memory
if "twin_mood" not in st.session_state: st.session_state.twin_mood = "Chill 😎"

# यूआरएल पैरामीटर्स ट्रैकिंग
query_params = st.query_params
if "page" not in query_params:
    st.session_state.current_view = "setup"
elif query_params["page"] == "chat" and st.session_state.current_view == "setup":
    st.session_state.current_view = "chat"

# --- 3. साइडबार ---
if st.session_state.current_view != "setup":
    with st.sidebar:
        st.markdown("## ⚡ JARVIS TERMINAL")
        if st.button("⬅️ SYSTEM RESET", help="Go back to setup"):
            st.query_params.clear()
            st.session_state.current_view = "setup"
            st.rerun()
            
        st.write("---")
        st.write(f"🤖 **ACTIVE ENGINE:** {st.session_state.saved_ai}")
        
        jarvis_toggle = st.radio(
            "🔴 JARVIS PROTOCOL STATUS:",
            ("Off", "On"),
            index=0 if st.session_state.jarvis_mode == "Off" else 1
        )
        if jarvis_toggle != st.session_state.jarvis_mode:
            st.session_state.jarvis_mode = jarvis_toggle
            st.toast(f"Jarvis Mode: {jarvis_toggle}", icon="🚀" if jarvis_toggle == "On" else "⏸️")
            st.rerun()

        st.write("---")
        # FEATURE 2: 🎭 EMOTION & MOOD SELECTOR
        st.markdown("### 🎭 TWIN EMOTION MODE")
        mood_choice = st.select_slider(
            "Select Current Mindset:",
            options=["Angry 😡", "Professional 💼", "Chill 😎", "Funny 🤪", "Sarcastic 🤖"],
            value=st.session_state.twin_mood
        )
        if mood_choice != st.session_state.twin_mood:
            st.session_state.twin_mood = mood_choice
            st.toast(f"Mood Synced: {mood_choice}", icon="🎭")
            st.rerun()

        st.write("---")
        if st.button("🏋️ BOT TRAINING STUDIO", use_container_width=True):
            st.session_state.current_view = "deep_train"
            st.rerun()
        if st.button("💬 MAIN CHAT ROOM", use_container_width=True):
            st.session_state.current_view = "chat"
            st.rerun()

# --- VIEW 1: SETUP PAGE ---
if st.session_state.current_view == "setup":
    st.title("🧠 MIRROR AI: Cyberpunk Core Setup")
    st.write("---")
    
    ai_choice = st.selectbox("Select AI Neural Engine:", ("Groq (Llama 3 - FREE)", "Google Gemini", "OpenAI (ChatGPT)"))
    key_input = st.text_input(f"Enter {ai_choice} API Key:", type="password", value=st.session_state.saved_key)
    
    master_input = st.text_area(
        "Train Your Twin (Write about yourself):",
        placeholder="जैसे: मेरा नाम गौरव है, मैं एक सॉफ्टवेयर डेवलपर हूँ और मुझे कोडिंग पसंद है...",
        value=st.session_state.master_training,
        height=150
    )
    
    if st.button("🔥 ACTIVATE DIGITAL TWIN & CORE SYSTEM 🚀", use_container_width=True):
        if not key_input or not master_input:
            st.error("⚠️ API Key और ट्रेनिंग डेटा दोनों अनिवार्य हैं!")
        else:
            st.session_state.saved_ai = ai_choice
            st.session_state.saved_key = key_input
            st.session_state.master_training = master_input
            st.session_state.current_view = "chat"
            st.query_params["page"] = "chat"
            st.rerun()

# --- VIEW 2: TRAINING PAGE ---
elif st.session_state.current_view == "deep_train":
    st.title("🏋️ Advanced Twin Training Studio")
    st.write("---")
    extra_text = st.text_area("✍️ Text Training Data:", value=st.session_state.master_training, height=150)
    audio_value = st.audio_input("🎙️ Voice Sync Descriptor:")
    if audio_value:
        st.success("🎙️ Voice print recorded into matrix memory!")
        st.session_state.voice_training = "\n[User provided an extra voice description.]"
    if st.button("💾 INJECT DATA INTO NEURAL MATRIX 🧠", use_container_width=True):
        st.session_state.master_training = extra_text
        st.session_state.current_view = "chat"
        st.rerun()

# --- VIEW 3: CHAT ROOM ---
elif st.session_state.current_view == "chat":
    st.title("🧠 Omni-Intelligent Jarvis Twin")
    
    # स्टेटस बार जो मूड दिखाता है
    st.markdown(f"**Current Personality State:** `{st.session_state.twin_mood}` Matrix Integration Active.")
    
    if st.session_state.jarvis_mode == "On":
        st.success("⚡ PROTOCOL JARVIS ACTIVE: Voice simulation & Action interception enabled.")
    else:
        st.info("💡 Standard Mode Active. (Activate Jarvis mode via sidebar for action overrides)")
        
    st.write("---")

    # चैट हिस्ट्री रेंडर
    for index, message in enumerate(st.session_state.messages):
        if message["role"] == "user":
            st.markdown(f'<div class="user-msg-container"><div class="user-msg">🧑 <b>You:</b><br>{message["content"]}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="twin-msg-container"><div class="twin-msg">🧠 <b>Mirror Twin:</b><br>{message["content"]}</div></div>', unsafe_allow_html=True)
            
            # जार्विस वॉयस रिप्लाई ऑटो-स्पीच सिस्टम
            if st.session_state.jarvis_mode == "On":
                tts_html = f"""
                <div style="display:flex; gap:10px; margin-top:5px;">
                    <button onclick="speak_{index}()" style="background-color: #ff007f; color: white; border: none; padding: 6px 12px; border-radius: 12px; cursor: pointer; font-size: 12px; font-shadow: 0 0 5px #ff007f;">🔊 Jarvis Override Response</button>
                </div>
                <script>
                    function speak_{index}() {{
                        var msg = new SpeechSynthesisUtterance();
                        msg.text = `{message["content"]}`;
                        msg.lang = 'hi-IN';
                        window.speechSynthesis.speak(msg);
                    }}
                </script>
                """
                components.html(tts_html, height=45)

    st.write("---")
    
    user_message = ""
    
    # वॉयस इनपुट बॉक्स यदि जार्विस मोड चालू है
    if st.session_state.jarvis_mode == "On":
        st.markdown("### 🎙️ Voice Terminal (Talk to Jarvis):")
        voice_input = st.audio_input("Speak Command:")
        if voice_input:
            user_message = "Jarvis, execute intercept: Simulate voice cloning or systemic application call control bypass."

    # रेगुलर चैट बॉक्स इनपुट
    chat_box_input = st.chat_input("Send encrypted matrix message...")
    if chat_box_input:
        user_message = chat_box_input

    if user_message:
        st.session_state.messages.append({"role": "user", "content": user_message})
        
        # --- FEATURE 3: 📧 LIVE JARVIS ACTION SIMULATOR TRIGER ---
        trigger_simulation = False
        sim_type = ""
        action_keywords = ["call", "phone", "message", "whatsapp", "भेजो", "फोन", "कॉल"]
        if st.session_state.jarvis_mode == "On" and any(keyword in user_message.lower() for keyword in action_keywords):
            trigger_simulation = True
            if "call" in user_message.lower() or "फोन" in user_message.lower() or "कॉल" in user_message.lower():
                sim_type = "CALL"
            else:
                sim_type = "MESSAGE"

        if trigger_simulation:
            with st.container():
                if sim_type == "CALL":
                    st.markdown(f"""
                    <div class="simulator-card">
                        <h3 style='color: #ff007f !important;'>📞 INTERCEPT STATUS: SIMULATING outgoing ENCRYPTED CALL</h3>
                        <p style='color: #00f2fe;'>Cloning Gaurav's Neural Voice Profile... 🎙️</p>
                        <p style='color: #ffffff; font-size: 12px;'>Establishing secure satellite uplink handshake via Matrix Node...</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="simulator-card">
                        <h3 style='color: #00f2fe !important;'>📨 INTERCEPT STATUS: DRAFTING WhatsApp SIMULATION</h3>
                        <p style='color: #ff007f;'>Text & Audio Synthesis: Matching <b>{st.session_state.twin_mood}</b> Persona Matrix.</p>
                        <p style='color: #ffffff; font-size: 12px;'>Payload encoded. Outbound transmission queue bypass active.</p>
                    </div>
                    """, unsafe_allow_html=True)
                time.sleep(2.5) # एनीमेशन फील कराने के लिए थोड़ा डिले

        # एआई प्रोसेसिंग कोर
        try:
            bot_reply = ""
            current_ai = st.session_state.saved_ai
            current_key = st.session_state.saved_key
            
            if not current_key:
                bot_reply = "⚠️ Core Key missing. Please click reset and insert valid neural encryption keys."
            else:
                # प्रॉम्प्ट में मूड (Feature 2) इंजेक्ट करना
                master_prompt = f"""
                SYSTEM ARCHITECTURE DIRECTIVE: You are Gaurav's absolute digital twin replica (Mirror Twin).
                TRAINING DATA MATRIX: {st.session_state.master_training}
                GAURAV'S VOCAL LOGS: {st.session_state.voice_training}
                
                CURRENT PERSONALITY MODIFIER MOOD: {st.session_state.twin_mood}
                JARVIS ACTION CONTROLLER STATUS: {st.session_state.jarvis_mode}
                
                CRITICAL INSTRUCTION: You MUST speak entirely in accordance with the current selected personality mood: '{st.session_state.twin_mood}'. If the mood is Angry, respond like a furious version of Gaurav. If Sarcastic, be witty and mock slightly. If Chill, be extremely laid back.
                
                If JARVIS ACTION CONTROLLER is 'On' and the user asks to call or message someone, creatively explain how you are cloning their vocal pattern, bypassing firewalls, and managing the call simulator seamlessly.
                
                User Message: {user_message}
                """
                
                if current_ai == "Google Gemini":
                    genai.configure(api_key=current_key)
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    response = model.generate_content(master_prompt)
                    bot_reply = response.text
                
                elif current_ai == "Groq (Llama 3 - FREE)":
                    client = Groq(api_key=current_key)
                    completion = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[{"role": "user", "content": master_prompt}]
                    )
                    bot_reply = completion.choices[0].message.content
                
                elif current_ai == "OpenAI (ChatGPT)":
                    client = openai.OpenAI(api_key=current_key)
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": master_prompt}]
                    )
                    bot_reply = response.choices[0].message.content

            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            st.rerun()
            
        except Exception as e:
            st.error(f"Matrix Core Decryption Failure: {e}")
    
