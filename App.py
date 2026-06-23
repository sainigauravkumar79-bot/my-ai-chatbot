import streamlit as st
import google.generativeai as genai
from groq import Groq
import openai
import streamlit.components.v1 as components

# --- पूरे पेज पर चैट फैलाने के लिए Config ---
st.set_page_config(page_title="MIRROR AI - Your Digital Twin", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")

# --- 1. प्रीमियम यूआई सीएसएस ---
st.markdown("""
<style>
    .user-msg-container { display: flex; justify-content: flex-end; margin-bottom: 10px; width: 100%; }
    .user-msg { 
        background: linear-gradient(135deg, #00c6ff, #0072ff); 
        color: white; padding: 14px 20px; border-radius: 22px 22px 4px 22px; 
        max-width: 85%; font-family: 'Helvetica Neue', sans-serif; box-shadow: 0px 4px 10px rgba(0,114,255,0.25);
    }
    .twin-msg-container { display: flex; flex-direction: column; align-items: flex-start; margin-bottom: 5px; width: 100%; }
    .twin-msg { 
        background: linear-gradient(135deg, #2c2d30, #1f2022); 
        color: #f5f5f5; padding: 14px 20px; border-radius: 22px 22px 22px 4px; 
        max-width: 85%; font-family: 'Helvetica Neue', sans-serif; border: 1px solid #3a3b3c; box-shadow: 0px 4px 10px rgba(0,0,0,0.4);
    }
</style>
""", unsafe_allow_html=True)

# --- 2. मेमोरी स्टोरेज (Session State) ---
if "saved_ai" not in st.session_state: st.session_state.saved_ai = "Google Gemini"
if "saved_key" not in st.session_state: st.session_state.saved_key = ""
if "master_training" not in st.session_state: st.session_state.master_training = ""
if "voice_training" not in st.session_state: st.session_state.voice_training = ""
if "messages" not in st.session_state: st.session_state.messages = []
if "current_view" not in st.session_state: st.session_state.current_view = "setup"
if "jarvis_mode" not in st.session_state: st.session_state.jarvis_mode = "Off"

# यूआरएल ट्रैकिंग
query_params = st.query_params
if "page" not in query_params:
    st.session_state.current_view = "setup"
elif query_params["page"] == "chat" and st.session_state.current_view == "setup":
    st.session_state.current_view = "chat"

# --- 3. साइडबार ---
if st.session_state.current_view != "setup":
    with st.sidebar:
        if st.button("⬅️ Back", help="Go to previous page"):
            if st.session_state.current_view == "deep_train":
                st.session_state.current_view = "chat"
            elif st.session_state.current_view == "chat":
                st.session_state.current_view = "setup"
                st.query_params.clear()
            st.rerun()
            
        st.markdown("## 🧠 Gemini Mirror")
        st.write(f"🤖 **Active Core:** {st.session_state.saved_ai}")
        st.write("---")
        
        jarvis_toggle = st.radio(
            "🔴 JARVIS MODE (Voice Clone & Call Control):",
            ("Off", "On"),
            index=0 if st.session_state.jarvis_mode == "Off" else 1
        )
        
        if jarvis_toggle != st.session_state.jarvis_mode:
            st.session_state.jarvis_mode = jarvis_toggle
            st.rerun()

        st.write("---")
        if st.button("🏋️ Training", use_container_width=True):
            st.session_state.current_view = "deep_train"
            st.rerun()
            
        if st.button("💬 Chat Room", use_container_width=True):
            st.session_state.current_view = "chat"
            st.rerun()
            
        st.write("---")
        if st.button("🔄 Reset / Logout", use_container_width=True):
            st.query_params.clear()
            st.session_state.current_view = "setup"
            st.session_state.messages = []
            st.session_state.saved_key = ""
            st.rerun()

# --- VIEW 1: SETUP PAGE ---
if st.session_state.current_view == "setup":
    st.title("🧠 MIRROR AI: Super-Brain Setup")
    st.write("---")
    
    ai_choice = st.selectbox("अपना एआई इंजन चुनें:", ("Groq (Llama 3 - FREE)", "Google Gemini", "OpenAI (ChatGPT)"))
    key_input = st.text_input(f"अपनी {ai_choice} API Key यहाँ पेस्ट करें:", type="password", value=st.session_state.saved_key)
    
    master_input = st.text_area(
        "अपने बारे में शुरूआती बातें लिखें:",
        placeholder="जैसे: मेरा नाम गौरव है...",
        value=st.session_state.master_training,
        height=150
    )
    
    if st.button("🔥 ACTIVATE TWIN 🚀", use_container_width=True):
        if not key_input or not master_input:
            st.error("कृपया API Key और ट्रेनिंग डेटा दोनों भरें!")
        else:
            st.session_state.saved_ai = ai_choice
            st.session_state.saved_key = key_input
            st.session_state.master_training = master_input
            st.session_state.current_view = "chat"
            st.query_params["page"] = "chat"
            st.rerun()

# --- VIEW 2: TRAINING PAGE ---
elif st.session_state.current_view == "deep_train":
    st.title("🏋️ Bot Training Studio")
    st.write("---")
    extra_text = st.text_area("✍️ Option 1: डिटेल्स यहाँ टाइप करें:", value=st.session_state.master_training, height=150)
    audio_value = st.audio_input("🎙️ अपनी आवाज़ में बोलकर डिटेल्स दें:")
    if audio_value:
        st.success("🎙️ वॉयस नोट रजिस्टर हो गया है!")
        st.session_state.voice_training = "\n[User provided an extra voice description.]"
    if st.button("💾 SAVE TRAINING & SYNC 🧠", use_container_width=True):
        st.session_state.master_training = extra_text
        st.session_state.current_view = "chat"
        st.rerun()

# --- VIEW 3: CHAT ROOM ---
elif st.session_state.current_view == "chat":
    st.title("🧠 Omni-Intelligent Digital Twin")
    
    if st.session_state.jarvis_mode == "On":
        st.success("⚡ JARVIS PROTOCOL ACTIVE: Full Voice System Enabled.")
    else:
        st.info("💡 Regular Mode Active. (Side bar से Jarvis Mode On कर सकते हैं)")
        
    st.write("---")

    # चैट हिस्ट्री रेंडर करना
    for index, message in enumerate(st.session_state.messages):
        if message["role"] == "user":
            st.markdown(f'<div class="user-msg-container"><div class="user-msg">🧑 <b>You:</b><br>{message["content"]}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="twin-msg-container"><div class="twin-msg">🧠 <b>Mirror Twin:</b><br>{message["content"]}</div></div>', unsafe_allow_html=True)
            
            if st.session_state.jarvis_mode == "On":
                tts_html = f"""
                <div style="display:flex; gap:10px; margin-top:5px;">
                    <button onclick="speak_{index}()" style="background-color: #ff4b4b; color: white; border: none; padding: 6px 12px; border-radius: 12px; cursor: pointer; font-size: 12px; font-family: sans-serif;">🔊 Jarvis Voice Reply</button>
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
    
    if st.session_state.jarvis_mode == "On":
        st.markdown("### 🎙️ Jarvis Voice Terminal:")
        voice_input = st.audio_input("कमांड बोलें:")
        if voice_input:
            user_message = "Jarvis Protocol Triggered: यूजर ने बोलकर कमांड दी है। उनके वॉयस टोन, फीलिंग्स और क्लोन का उपयोग करके कॉल या वॉयस मैसेज भेजने की स्थिति संभालो।"

    chat_box_input = st.chat_input("ट्विन से कुछ भी कहें...")
    if chat_box_input:
        user_message = chat_box_input

    if user_message:
        st.session_state.messages.append({"role": "user", "content": user_message})

        try:
            bot_reply = ""
            current_ai = st.session_state.saved_ai
            current_key = st.session_state.saved_key
            
            if not current_key:
                bot_reply = "⚠️ कृपया साइडबार में 'Back' बटन दबाकर सेटअप पेज पर जाएं और अपनी API Key दोबारा दर्ज करें।"
            else:
                master_prompt = f"""
                MASTER DIRECTIVE: Replicate user's behavior based on this data: 
                TEXT MEMORY: {st.session_state.master_training}
                VOICE STATUS: {st.session_state.voice_training}
                JARVIS MODE STATUS: {st.session_state.jarvis_mode}
                
                If JARVIS MODE is 'On', act as a fully synchronized voice clone and app controller. If the user commands to make a call or send a voice note, simulate the voice cloning system. Confirm you are utilizing their vocal pattern, feelings, and style.
                If JARVIS MODE is 'Off', just reply normally as a digital twin.
                
                User Message: {user_message}
                """
                
                if current_ai == "Google Gemini":
                    genai.configure(api_key=current_key)
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    response = model.generate_content(master_prompt)
                    bot_reply = response.text
                
                elif current_ai == "Groq (Llama 3 - FREE)":
                    client = Groq(api_key=current_key)
                    # 🔥 यहाँ बंद हुए मॉडल को नए 'llama-3.1-8b-instant' मॉडल से बदल दिया गया है
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
            st.error(f"API Error: {e}")
    
