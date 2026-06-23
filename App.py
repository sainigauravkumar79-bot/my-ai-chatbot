import streamlit as st
import google.generativeai as genai
from groq import Groq
import openai
import streamlit.components.v1 as components

# --- पूरे पेज पर चैट फैलाने के लिए Config ---
st.set_page_config(page_title="MIRROR AI - Your Digital Twin", page_icon="🧠", layout="wide", initial_sidebar_state="collapsed")

# --- 1. एडवांस कस्टम CSS स्टाइल (Custom Sidebar और यूआई) ---
st.markdown("""
<style>
    /* डिफ़ॉल्ट साइडबार को छुपाना */
    [data-testid="stSidebar"] { display: none; }
    [data-testid="collapsedControl"] { display: none; }
    
    /* चैट बबल्स फुल विड्थ */
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

# --- 2. परमानेंट मेमोरी स्टोरेज (Session State) ---
if "saved_ai" not in st.session_state: st.session_state.saved_ai = "Google Gemini"
if "saved_key" not in st.session_state: st.session_state.saved_key = ""
if "master_training" not in st.session_state: st.session_state.master_training = ""
if "voice_training" not in st.session_state: st.session_state.voice_training = ""
if "messages" not in st.session_state: st.session_state.messages = []
if "menu_open" not in st.session_state: st.session_state.menu_open = False
if "current_view" not in st.session_state: st.session_state.current_view = "chat" # chat, deep_train, setup

# हार्डवेयर या यूआरएल ट्रैकिंग
query_params = st.query_params
if "page" not in query_params:
    st.session_state.current_view = "setup"
elif query_params["page"] == "chat" and st.session_state.current_view == "setup":
    st.session_state.current_view = "chat"

# --- 3. नैविगेशन हेडर (Back Arrow + 3 Lines Menu) ---
if st.session_state.current_view != "setup":
    col_nav1, col_nav2, _ = st.columns([1, 1, 10])
    
    with col_nav1:
        # बैक एरो बटन - पिछले पेज पर जाने के लिए
        if st.button("⬅️", help="Go Back"):
            if st.session_state.current_view == "deep_train":
                st.session_state.current_view = "chat"
            elif st.session_state.current_view == "chat":
                st.session_state.current_view = "setup"
                st.query_params.clear()
            st.rerun()
            
    with col_nav2:
        # 3 लाइन्स (Hamburger) मेन्यू बटन - ओपन / क्लोज करने के लिए
        if st.button("☰", help="Menu"):
            st.session_state.menu_open = not st.session_state.menu_open
            st.rerun()

    # अगर मेन्यू ओपन है, तो स्क्रीन पर फुल लेंथ छोटा मेन्यू पैनल दिखेगा
    if st.session_state.menu_open:
        st.markdown("---")
        st.markdown("### 📋 Navigation Menu")
        if st.button("🧠 Deep Training (Add Text & Voice Details)", use_container_width=True):
            st.session_state.current_view = "deep_train"
            st.session_state.menu_open = False # जाने के बाद मेन्यू क्लोज
            st.rerun()
        if st.button("🔄 Reset AI / Logout", use_container_width=True):
            st.query_params.clear()
            st.session_state.current_view = "setup"
            st.session_state.messages = []
            st.session_state.menu_open = False
            st.rerun()
        st.markdown("---")

# --- 4. व्यू कंट्रोलर (Views Switcher) ---

# --- VIEW A: SETUP PAGE ---
if st.session_state.current_view == "setup":
    st.title("🧠 MIRROR AI: Super-Brain Setup")
    st.write("अपने एआई को अपनी लाइफस्टाइल सिखाने के लिए क्रेडेंशियल्स डालें।")
    st.write("---")
    
    ai_choice = st.selectbox("अपना एआई इंजन चुनें:", ("Google Gemini", "Groq (Llama 3 - FREE)", "OpenAI (ChatGPT)"))
    key_input = st.text_input(f"अपनी {ai_choice} API Key यहाँ पेस्ट करें:", type="password", value=st.session_state.saved_key)
    
    master_input = st.text_area(
        "अपने बारे में शुरूआती बातें लिखें:",
        placeholder="जैसे: मेरा नाम गौरव है। मैं काम के समय प्रोफेशनल और दोस्तों के साथ चिल रहता हूँ...",
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

# --- VIEW B: DEEP TRAINING PAGE (New Feature - Text & Voice!) ---
elif st.session_state.current_view == "deep_train":
    st.title("🚀 Deep Training Studio")
    st.write("यहाँ अपने बारे में और अधिक बारीकियाँ जोड़ें ताकि आपका बॉट और ज़्यादा स्मार्ट बन सके।")
    st.write("---")
    
    # 1. एक्स्ट्रा टेक्स्ट इनपुट
    extra_text = st.text_area(
        "✍️ अपने बारे में और डिटेल्स यहाँ टाइप करें (जैसे आपकी पसंद, नापसंद, रूटीन):",
        value=st.session_state.master_training,
        height=150
    )
    
    # 2. वॉयस रिकॉर्डिंग इनपुट (Audio Recorder Component)
    st.markdown("### 🎙️ या अपनी आवाज़ में बोलकर डिटेल्स रिकॉर्ड करें")
    audio_value = st.audio_input("रिकॉर्ड बटन पर क्लिक करें और बोलना शुरू करें:")
    
    if audio_value:
        st.audio(audio_value, format="audio/wav")
        st.success("🤖 वॉयस नोट जुड़ गया! (भविष्य में इसे सीधे टेक्स्ट में बदला जा सकेगा)")
        st.session_state.voice_training = "\n[User provided a voice briefing detailing their personality/mood for extra accuracy.]"

    st.write("---")
    if st.button("💾 SAVE & RE-SYNC CORE 🧠", use_container_width=True):
        st.session_state.master_training = extra_text
        st.success("आपकी नयी बारीकियाँ एआई कोर में सेव हो चुकी हैं!")
        st.session_state.current_view = "chat"
        st.rerun()

# --- VIEW C: CENTRAL CHAT ROOM (All Features Retained) ---
elif st.session_state.current_view == "chat":
    st.title("🧠 Omni-Intelligent Digital Twin")
    st.write("---")

    # चैट हिस्ट्री दिखाना
    for index, message in enumerate(st.session_state.messages):
        if message["role"] == "user":
            st.markdown(f'<div class="user-msg-container"><div class="user-msg">🧑 <b>You:</b><br>{message["content"]}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="twin-msg-container"><div class="twin-msg">🧠 <b>Mirror Twin:</b><br>{message["content"]}</div></div>', unsafe_allow_html=True)
            
            # पुराना क्रैश-प्रूफ शेयर बटन सुरक्षित है
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
            
            # प्रॉम्प्ट में वॉयस का सिंक भी जोड़ दिया ताकि इंटेलिजेंस बढ़े
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
            
