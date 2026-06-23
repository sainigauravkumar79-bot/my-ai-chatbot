import streamlit as st
import google.generativeai as genai
from groq import Groq
import openai
import streamlit.components.v1 as components

# --- पूरे पेज पर चैट फैलाने के लिए Config (शुरुआत में साइडबार खुला रहेगा) ---
st.set_page_config(page_title="MIRROR AI - Your Digital Twin", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")

# --- 1. प्रीमियम यूआई सीएसएस (चैट बबल्स फुल विड्थ) ---
st.markdown("""
<style>
    /* चैट बबल्स फुल विड्थ और प्रीमियम लुक */
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

# यूआरएल ट्रैकिंग
query_params = st.query_params
if "page" not in query_params:
    st.session_state.current_view = "setup"
elif query_params["page"] == "chat" and st.session_state.current_view == "setup":
    st.session_state.current_view = "chat"

# --- 3. असली नैटिव साइडबार (जैसे जेमिनी ऐप में है) ---
if st.session_state.current_view != "setup":
    with st.sidebar:
        # सबसे ऊपर बैक एरो बटन पिछले पेज पर जाने के लिए
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
        
        # 🎯 आपका खास 'Training' ऑप्शन जिसपर क्लिक करने से नया पेज खुलेगा
        if st.button("🏋️ Training", use_container_width=True, help="Train your bot with Text & Voice"):
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
            st.rerun()

# --- 4. व्यू कंट्रोलर (Views Switcher) ---

# --- VIEW 1: SETUP PAGE ---
if st.session_state.current_view == "setup":
    st.title("🧠 MIRROR AI: Super-Brain Setup")
    st.write("---")
    
    ai_choice = st.selectbox("अपना एआई इंजन चुनें:", ("Google Gemini", "Groq (Llama 3 - FREE)", "OpenAI (ChatGPT)"))
    key_input = st.text_input(f"अपनी {ai_choice} API Key यहाँ पेस्ट करें:", type="password", value=st.session_state.saved_key)
    
    master_input = st.text_area(
        "अपने बारे में शुरूआती बातें लिखें:",
        placeholder="जैसे: मेरा नाम गौरव है। मैं काम के समय प्रोफेशनल और दोस्तों के साथ चil रहता हूँ...",
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

# --- VIEW 2: NEW TRAINING PAGE (Text & Voice Options Here!) ---
elif st.session_state.current_view == "deep_train":
    st.title("🏋️ Bot Training Studio")
    st.write("यहाँ अपने बॉट को और डिटेल्स देकर सिखाएं ताकि वह आपकी तरह सोचना शुरू करे।")
    st.write("---")
    
    # ऑप्शन 1: टेक्स्ट डिटेल्स
    extra_text = st.text_area(
        "✍️ Option 1: अपने बारे में और डिटेल्स यहाँ टाइप करें:",
        value=st.session_state.master_training,
        height=150
    )
    
    # ऑप्शन 2: वॉयस रिकॉर्डिंग
    st.markdown("### 🎙️ Option 2: अपनी आवाज़ में बोलकर डिटेल्स दें")
    audio_value = st.audio_input("रिकॉर्ड बटन दबाएं और जो सिखाना है बोलें:")
    
    if audio_value:
        st.audio(audio_value, format="audio/wav")
        st.success("🎙️ वॉयस नोट रजिस्टर हो गया है!")
        st.session_state.voice_training = "\n[User provided an extra voice description about their identity/behavior for deep learning.]"

    st.write("---")
    if st.button("💾 SAVE TRAINING & SYNC 🧠", use_container_width=True):
        st.session_state.master_training = extra_text
        st.success("बॉट ने नया डेटा सीख लिया है!")
        st.session_state.current_view = "chat"
        st.rerun()

# --- VIEW 3: CENTRAL CHAT ROOM ---
elif st.session_state.current_view == "chat":
    st.title("🧠 Omni-Intelligent Digital Twin")
    st.write("---")

    # चैट हिस्ट्री दिखाना
    for index, message in enumerate(st.session_state.messages):
        if message["role"] == "user":
            st.markdown(f'<div class="user-msg-container"><div class="user-msg">🧑 <b>You:</b><br>{message["content"]}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="twin-msg-container"><div class="twin-msg">🧠 <b>Mirror Twin:</b><br>{message["content"]}</div></div>', unsafe_allow_html=True)
            
            # पुराना क्रैश-प्रूफ शेयर बटन
            html_btn = f"""
            <button onclick="share()" style="background-color: #3a3b3c; color: #e4e6eb; border: none; padding: 6px 12px; border-radius: 12px; cursor: pointer; font-size: 12px; display: flex; align-items: center; gap: 5px; font-family: sans-serif;">🔗 Share / Send to Apps</button>
            <script>
                function share() {{
                    if (navigator.share) {{
                        navigator.share({{
                            title: 'Mirror AI',
                            text: `{message["content"]}`
                        }});
                    }} else {{
                        window.open('https://wa.me/?text=' + encodeURIComponent(`{message["content"]}`), '_blank');
                    }}
                }}
            </script>
            """
            components.html(html_btn, height=35)

    # चैट इनपुट बॉक्स
    if user_message := st.chat_input("अपने ट्विन से कुछ भी कहें..."):
        st.markdown(f'<div class="user-msg-container"><div class="user-msg">🧑 <b>You:</b><br>{user_message}</div></div>', unsafe_allow_html=True)
        st.session_state.messages.append({"role": "user", "content": user_message})

        try:
            bot_reply = ""
            current_ai = st.session_state.saved_ai
            current_key = st.session_state.saved_key
            
            master_prompt = f"""
            MASTER DIRECTIVE: Replicate user's behavior based on this data: 
            TEXT MEMORY: {st.session_state.master_training}
            VOICE STATUS: {st.session_state.voice_training}
            
            DYNAMIC LOGIC: Auto-detect if message is professional or casual and reply in their style instantly. Do not mention modes.
            User Message: {user_message}
            """
            
            ai_messages = [{"role": "user", "content": master_prompt}]
            for msg in st.session_state.messages:
                ai_messages.append({"role": msg["role"], "content": msg["content"]})
            
            if current_ai == "Google Gemini":
                genai.configure(api_key=current_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                full_context = "\n".join([f"{m['role']}: {m['content']}" for m in ai_messages])
                response = model.generate_content(full_context)
                bot_reply = response.text
            
            elif current_ai == "Groq (Llama 3 - FREE)":
                client = Groq(api_key=current_key)
                formatted_msgs = [{"role": "user" if m["role"] == "user" else "assistant", "content": m["content"]} for m in ai_messages]
                completion = client.chat.completions.create(model="llama3-8b-8192", messages=formatted_msgs)
                bot_reply = completion.choices[0].message.content
            
            elif current_ai == "OpenAI (ChatGPT)":
                client = openai.OpenAI(api_key=current_key)
                formatted_msgs = [{"role": "user" if m["role"] == "user" else "assistant", "content": m["content"]} for m in ai_messages]
                response = client.chat.completions.create(model="gpt-3.5-turbo", messages=formatted_msgs)
                bot_reply = response.choices[0].message.content

            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            st.rerun()
            
        except Exception as e:
            st.error(f"एरर आया: {e}")
    
