import streamlit as st
import openai
import google.generativeai as genai
from groq import Groq

st.set_page_config(page_title="Gaurav's Multi-AI Chatbot", page_icon="🤖")

# --- 1. दाईं (Right) और बाईं (Left) तरफ मैसेज दिखाने के लिए CSS ---
st.markdown("""
<style>
    .user-msg-container {
        display: flex;
        justify-content: flex-end;
        margin-bottom: 10px;
    }
    .user-msg {
        background-color: #2b5c8f;
        color: white;
        padding: 10px 15px;
        border-radius: 15px 15px 0px 15px;
        max-width: 75%;
        text-align: left;
    }
    .bot-msg-container {
        display: flex;
        justify-content: flex-start;
        margin-bottom: 10px;
    }
    .bot-msg {
        background-color: #2d2d2d;
        color: #f0f2f6;
        padding: 10px 15px;
        border-radius: 15px 15px 15px 0px;
        max-width: 75%;
        text-align: left;
        border: 1px solid #4a4a4a;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. मेमोरी (Session State) सेट करना ---
if "saved_ai" not in st.session_state:
    st.session_state.saved_ai = "Google Gemini"
if "saved_key" not in st.session_state:
    st.session_state.saved_key = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 3. ब्राउज़र URL / फ़ोन बैक बटन सपोर्ट ---
query_params = st.query_params

if "page" not in query_params:
    st.session_state.keys_saved = False
elif query_params["page"] == "chat":
    st.session_state.keys_saved = True

# --- 4. पहला पेज: SETUP PAGE ---
if not st.session_state.keys_saved:
    st.title("🔑 Gaurav's AI Setup")
    st.write("चैट शुरू करने से पहले अपना AI और API Key सेट करें।")
    
    ai_choice = st.selectbox(
        "कौन सा AI इस्तेमाल करना चाहते हैं?",
        ("Google Gemini", "Groq (Llama 3 - FREE)", "OpenAI (ChatGPT)")
    )
    
    key_input = st.text_input(f"अपनी {ai_choice} API Key यहाँ पेस्ट करें:", type="password")
    
    if st.button("OK - Save & Start Chatting 🚀", use_container_width=True):
        if not key_input:
            st.error(f"कृपया आगे बढ़ने के लिए {ai_choice} की API Key ज़रूर डालें!")
        else:
            st.session_state.saved_ai = ai_choice
            st.session_state.saved_key = key_input
            st.query_params["page"] = "chat"
            st.rerun()

# --- 5. दूसरा पेज: NEW CHAT PAGE ---
else:
    with st.sidebar:
        st.header("⚙️ Settings")
        st.write(f"🤖 **Active AI:** {st.session_state.saved_ai}")
        st.write("---")
        if st.button("🔄 Change AI / Reset"):
            st.query_params.clear()
            st.rerun()
        st.write("💡 **टिप:** आप अपने **फ़ोन का बैक बटन** दबाकर भी वापस जा सकते हैं!")

    st.title(f"🤖 Gaurav's Chat Room")
    st.write(f"शुरू करें बातचीत ({st.session_state.saved_ai} के साथ)")
    st.write("---")

    # कस्टम CSS के ज़रिये चैट हिस्ट्री दिखाना
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f'<div class="user-msg-container"><div class="user-msg">🧑 <b>You:</b><br>{message["content"]}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-msg-container"><div class="bot-msg">🤖 <b>AI:</b><br>{message["content"]}</div></div>', unsafe_allow_html=True)

    # चैट इनपुट बॉक्स
    if user_message := st.chat_input("यहाँ अपना सवाल लिखें..."):
        # यूजर का मैसेज तुरंत दाईं तरफ दिखाना और सेव करना
        st.markdown(f'<div class="user-msg-container"><div class="user-msg">🧑 <b>You:</b><br>{user_message}</div></div>', unsafe_allow_html=True)
        st.session_state.messages.append({"role": "user", "content": user_message})

        try:
            bot_reply = ""
            current_ai = st.session_state.saved_ai
            current_key = st.session_state.saved_key
            
            if current_ai == "Google Gemini":
                genai.configure(api_key=current_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                response = model.generate_content(user_message)
                bot_reply = response.text
            
            elif current_ai == "Groq (Llama 3 - FREE)":
                client = Groq(api_key=current_key)
                completion = client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[{"role": "user", "content": user_message}]
                )
                bot_reply = completion.choices[0].message.content
            
            elif current_ai == "OpenAI (ChatGPT)":
                client = openai.OpenAI(api_key=current_key)
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": user_message}]
                )
                bot_reply = response.choices[0].message.content

            # AI का जवाब बाईं तरफ सेव करना
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            st.rerun()
            
        except Exception as e:
            st.error(f"एरर आया! एरर: {e}")
                
