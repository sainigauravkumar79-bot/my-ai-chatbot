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
if "master_training" not in st.session_state: st.session_state.master_training = ""
if "messages" not in st.session_state: st.session_state.messages = []

# हार्डवेयर बैक बटन ट्रैकिंग
query_params = st.query_params
if "page" not in query_params:
    st.session_state.keys_saved = False
elif query_params["page"] == "chat":
    st.session_state.keys_saved = True

# --- 3. पहला पेज: MASTER SETUP PAGE ---
if not st.session_state.keys_saved:
    st.title("🧠 MIRROR AI: Super-Brain Setup")
    st.write("अपने एआई को अपनी पूरी लाइफस्टाइल, काम और बातचीत का तरीका एक बार में सिखाएं।")
    st.write("---")
    
    ai_choice = st.selectbox(
        "अपना एआई इंजन चुनें:",
        ("Google Gemini", "Groq (Llama 3 - FREE)", "OpenAI (ChatGPT)")
    )
    key_input = st.text_input(f"अपनी {ai_choice} API Key यहाँ पेस्ट करें:", type="password", value=st.session_state.saved_key)
    
    st.write("---")
    st.subheader("📝 मास्टर ट्रेनिंग डेटा (Master Knowledge Base)")
    
    master_input = st.text_area(
        "अपने बारे में सब कुछ एक साथ लिखें (आपका बिजनेस, आपकी पर्सनल लाइफ, दोस्तों से बात करने का स्टाइल आदि सब मिक्स):",
        placeholder="जैसे: मेरा नाम गौरव है। मेरा एक बिजनेस है जहाँ मैं बहुत प्रोफेशनल रहता हूँ। लेकिन पर्सनल लाइफ में मैं दोस्तों से 'भाई' बोलता हूँ और मज़ाक करता हूँ। जब मैं कोई काम बोलूँ तो समझदारी से काम करना, जब गपशप करूँ तो दोस्त बन जाना...",
        value=st.session_state.master_training,
        height=180
    )
    
    st.write("---")
    if st.button("🔥 ACTIVATE INTELLIGENT DIGITAL TWIN 🚀", use_container_width=True):
        if not key_input:
            st.error("आगे बढ़ने के लिए API Key डालना अनिवार्य है!")
        elif not master_input:
            st.error("अपने ट्विन को इंटेलिजेंट बनाने के लिए मास्टर ट्रेनिंग डेटा लिखना ज़रूरी है!")
        else:
            st.session_state.saved_ai = ai_choice
            st.session_state.saved_key = key_input
            st.session_state.master_training = master_input
            st.query_params["page"] = "chat"
            st.rerun()

# --- 4. दूसरा पेज: CENTRAL CHAT ROOM (ALL-IN-ONE BOT) ---
else:
    with st.sidebar:
        st.header("⚙️ Settings")
        if st.button("🔄 री-ट्रेन करें / लॉगआउट"):
            st.query_params.clear()
            st.rerun()

    st.title("🧠 Your Omni-Intelligent Digital Twin")
    st.info("💡 यह सिंगल बॉट आपके मैसेज के कॉन्टेक्स्ट को खुद समझेगा और उसी हिसाब से रिएक्ट करेगा।")
    st.write("---")

    # चैट हिस्ट्री दिखाना
    for index, message in enumerate(st.session_state.messages):
        if message["role"] == "user":
            st.markdown(f'<div class="user-msg-container"><div class="user-msg">🧑 <b>You:</b><br>{message["content"]}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="twin-msg-container">
                <div class="twin-msg">🧠 <b>Mirror Twin:</b><br>{message["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # फिक्स्ड क्रैश-प्रूफ नेटिव शेयर बटन
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
    if user_message := st.chat_input("अपने ट्विन से कुछ भी कहें (काम, गपशप या ड्राफ्टिंग)..."):
        st.markdown(f'<div class="user-msg-container"><div class="user-msg">🧑 <b>You:</b><br>{user_message}</div></div>', unsafe_allow_html=True)
        st.session_state.messages.append({"role": "user", "content": user_message})

        try:
            bot_reply = ""
            current_ai = st.session_state.saved_ai
            current_key = st.session_state.saved_key
            
            # 🔥 द अल्टीमेट ओम्नी-प्रॉम्प्ट (Omni-Prompt) जो एआई को खुद सोचने और सिचुएशन समझने पर मजबूर करता है
            ai_messages = [
                {
                    "role": "user", 
                    "content": f"""
                    MASTER DIRECTIVE: You are the absolute digital replica (twin) of the user. 
                    Here is your complete life, professional, and personal background: 
                    {st.session_state.master_training}
                    
                    DYNAMIC LOGIC: 
                    1. Analyze the context of the user's latest message and the entire chat history.
                    2. If the user is asking to draft something for work, clients, or business, automatically adopt an intelligent, sharp, and professional tone.
                    3. If the user is chatting casually, emotional, or talking about friends/family, immediately shift to their personal, warm, or humorous lifestyle tone.
                    4. Do NOT tell the user which mode you are choosing. Just naturally think and respond exactly how they would in that specific scenario.
                    5. Learn from their messaging style continuously from the conversation history below.
                    """
                }
            ]
            
            # रियल-टाइम ऑटो-लर्निंग के लिए पूरी चैट हिस्ट्री जोड़ना
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
            st.error(f"मिरर कोर एरर: {e}")
                
