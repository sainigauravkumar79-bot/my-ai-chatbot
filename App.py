import streamlit as st
import google.generativeai as genai
from groq import Groq
import openai
import streamlit.components.v1 as components

# --- पूरे पेज पर चैट फैलाने के लिए Config ---
st.set_page_config(page_title="MIRROR AI - Your Digital Twin", page_icon="🧠", layout="wide", initial_sidebar_state="collapsed")

# --- 1. प्रीमियम फुल-पेज चैट स्टाइल ---
st.markdown("""
<style>
    /* साइडबार को छुपाना */
    [data-testid="stSidebar"] { display: none; }
    [data-testid="collapsedControl"] { display: block; }
    
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
if "twin_personality" not in st.session_state: st.session_state.twin_personality = ""
if "messages" not in st.session_state: st.session_state.messages = []

# हार्डवेयर बैक बटन ट्रैकिंग
query_params = st.query_params
if "page" not in query_params:
    st.session_state.keys_saved = False
elif query_params["page"] == "chat":
    st.session_state.keys_saved = True

# --- 3. पहला पेज: SETUP PAGE ---
if not st.session_state.keys_saved:
    st.title("🔑 Gaurav's AI Setup")
    st.write("चैट शुरू करने से पहले अपना AI और API Key सेट करें।")
    
    ai_choice = st.selectbox(
        "कौन सा AI इस्तेमाल करना चाहते हैं?",
        ("Google Gemini", "Groq (Llama 3 - FREE)", "OpenAI (ChatGPT)")
    )
    key_input = st.text_input(f"अपनी {ai_choice} API Key यहाँ पेस्ट करें:", type="password")
    
    personality_input = st.text_area(
        "एआई को अपने बारे में शुरूआती ट्रेनिंग दें:",
        placeholder="जैसे: मेरा नाम गौरव है। मैं दोस्तों से 'भाई' करके बात करता हूँ...",
        height=100
    )
    
    if st.button("OK - Save & Start Chatting 🚀", use_container_width=True):
        if not key_input:
            st.error(f"कृपया आगे बढ़ने के लिए {ai_choice} की API Key ज़रूर डालें!")
        else:
            st.session_state.saved_ai = ai_choice
            st.session_state.saved_key = key_input
            st.session_state.twin_personality = personality_input
            st.query_params["page"] = "chat"
            st.rerun()

# --- 4. दूसरा पेज: NEW FULL PAGE CHAT WITH AUTO-LEARNING ---
else:
    with st.sidebar:
        st.header("⚙️ Settings")
        if st.button("🔄 Change AI / Reset"):
            st.query_params.clear()
            st.rerun()

    st.title(f"🤖 {st.session_state.saved_ai} Chatroom")
    st.write("---")

    # चैट हिस्ट्री दिखाना
    for index, message in enumerate(st.session_state.messages):
        if message["role"] == "user":
            st.markdown(f'<div class="user-msg-container"><div class="user-msg">🧑 <b>You:</b><br>{message["content"]}</div></div>', unsafe_allow_html=True)
        else:
            # मैसेज डिस्प्ले
            st.markdown(f"""
            <div class="twin-msg-container">
                <div class="twin-msg">🧠 <b>Mirror Twin:</b><br>{message["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # नेटिव शेयर पॉप-अप बटन (सुरक्षित HTML Component के ज़रिए)
            # यह क्रैश-प्रूफ है और सीधा फोन के शेयर सिस्टम को ट्रिगर करेगा
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
    if user_message := st.chat_input("यहाँ अपना सवाल लिखें..."):
        st.markdown(f'<div class="user-msg-container"><div class="user-msg">🧑 <b>You:</b><br>{user_message}</div></div>', unsafe_allow_html=True)
        st.session_state.messages.append({"role": "user", "content": user_message})

        try:
            bot_reply = ""
            current_ai = st.session_state.saved_ai
            current_key = st.session_state.saved_key
            
            # 🔥 सुपर मास्टर प्रॉम्प्ट: यह पुरानी चैट हिस्ट्री भी साथ भेजेगा ताकि रोबोट रोज़ की बातों से सीखे!
            ai_messages = [
                {
                    "role": "user" if current_ai != "Google Gemini" else "user", 
                    "content": f"MASTER INSTRUCTION: You are the user's digital twin. Replicate their exact language, memory, and behavior based on this initial data: {st.session_state.twin_personality}. Also, analyze the following conversation history to learn their latest talking style and responses in real-time."
                }
            ]
            
            # पुरानी पूरी चैट हिस्ट्री को जोड़ना (ताकि एआई रोज़ की बातों से खुद को अपडेट करे)
            for msg in st.session_state.messages:
                ai_messages.append({"role": msg["role"], "content": msg["content"]})
            
            if current_ai == "Google Gemini":
                genai.configure(api_key=current_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                # जेमिनी के लिए सारे मैसेजेस को कंबाइन करना
                full_context = "\n".join([f"{m['role']}: {m['content']}" for m in ai_messages])
                response = model.generate_content(full_context)
                bot_reply = response.text
            
            elif current_ai == "Groq (Llama 3 - FREE)":
                client = Groq(api_key=current_key)
                # ग्रोक के मैसेजेस फ़ॉर्मेट को सही करना
                formatted_msgs = [{"role": "user" if m["role"] == "user" else "assistant", "content": m["content"]} for m in ai_messages]
                completion = client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=formatted_msgs
                )
                bot_reply = completion.choices[0].message.content
            
            elif current_ai == "OpenAI (ChatGPT)":
                client = openai.OpenAI(api_key=current_key)
                formatted_msgs = [{"role": "user" if m["role"] == "user" else "assistant", "content": m["content"]} for m in ai_messages]
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=formatted_msgs
                )
                bot_reply = response.choices[0].message.content

            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            st.rerun()
            
        except Exception as e:
            st.error(f"एरर आया! एरर: {e}")
                                
