import streamlit as st
import google.generativeai as genai
from groq import Groq
import openai
import urllib.parse

# --- पूरे पेज पर चैट फैलाने के लिए Config ---
st.set_page_config(page_title="MIRROR AI - Your Digital Twin", page_icon="🧠", layout="wide", initial_sidebar_state="collapsed")

# --- 1. प्रीमियम फुल-पेज चैट और गोल शेयर बटन स्टाइल ---
st.markdown("""
<style>
    /* साइडबार को छुपाना ताकि चैट पूरे पेज पर आए */
    [data-testid="stSidebar"] {
        display: none;
    }
    [data-testid="collapsedControl"] {
        display: block;
    }
    
    /* चैट बबल्स को पूरी चौड़ाई (Full Width) देना */
    .user-msg-container { display: flex; justify-content: flex-end; margin-bottom: 10px; width: 100%; }
    .user-msg { 
        background: linear-gradient(135deg, #00c6ff, #0072ff); 
        color: white; padding: 14px 20px; border-radius: 22px 22px 4px 22px; 
        max-width: 85%; font-family: 'Helvetica Neue', sans-serif; box-shadow: 0px 4px 10px rgba(0,114,255,0.25);
    }
    .twin-msg-container { display: flex; flex-direction: column; align-items: flex-start; margin-bottom: 15px; width: 100%; }
    .twin-msg { 
        background: linear-gradient(135deg, #2c2d30, #1f2022); 
        color: #f5f5f5; padding: 14px 20px; border-radius: 22px 22px 22px 4px; 
        max-width: 85%; font-family: 'Helvetica Neue', sans-serif; border: 1px solid #3a3b3c; box-shadow: 0px 4px 10px rgba(0,0,0,0.4);
    }
    
    /* छोटा और गोल शेयर बटन जो चैट से बिल्कुल सटा हुआ रहेगा */
    .share-btn {
        background-color: #3a3b3c;
        color: #e4e6eb;
        border: none;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
        margin-top: 6px;
        margin-left: 5px;
        transition: background 0.2s;
    }
    .share-btn:hover {
        background-color: #4e4f50;
    }
</style>

<script>
    // मोबाइल के सभी ऐप्स पर शेयर करने का जादुई फंक्शन
    function shareContent(text) {
        if (navigator.share) {
            navigator.share({
                title: 'Mirror AI Response',
                text: text
            }).catch(console.error);
        } else {
            // बैकअप अगर ब्राउज़र सपोर्ट न करे
            window.open('https://wa.me/?text=' + encodeURIComponent(text), '_blank');
        }
    }
</script>
""", unsafe_allow_html=True)

# --- 2. परमानेंट मेमोरी स्टोरेज (Session State) ---
if "saved_ai" not in st.session_state: st.session_state.saved_ai = "Google Gemini"
if "saved_key" not in st.session_state: st.session_state.saved_key = ""
if "twin_personality" not in st.session_state: st.session_state.twin_personality = ""
if "messages" not in st.session_state: st.session_state.messages = []

# हार्डवेयर बैक बटन के लिए यूआरएल ट्रैकिंग
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
        "एआई को अपने बारे में लिखकर बताएं (ट्रेनिंग डेटा):",
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

# --- 4. दूसरा पेज: NEW FULL PAGE CHAT ---
else:
    # साइडबार को छोटा कर दिया है, टॉप लेफ्ट बटन दबाकर देखा जा सकता है
    with st.sidebar:
        st.header("⚙️ Settings")
        st.write(f"🤖 **Active AI:** {st.session_state.saved_ai}")
        if st.button("🔄 Change AI / Reset"):
            st.query_params.clear()
            st.rerun()

    st.title(f"🤖 {st.session_state.saved_ai} Chatroom")
    st.write("---")

    # चैट हिस्ट्री (फुल विड्थ और गोल बटन के साथ)
    for index, message in enumerate(st.session_state.messages):
        if message["role"] == "user":
            st.markdown(f'<div class="user-msg-container"><div class="user-msg">🧑 <b>You:</b><br>{message["content"]}</div></div>', unsafe_allow_html=True)
        else:
            # सुरक्षित क्लीन टेक्स्ट बनाना बिना इनवर्टेड कॉमा की गड़बड़ के
            clean_text = message["content"].replace("'", "\\'").replace("\n", " ")
            
            # चैट और उसके नीचे सटा हुआ छोटा गोल बटन
            st.markdown(f"""
            <div class="twin-msg-container">
                <div class="twin-msg">🧠 <b>Mirror Twin:</b><br>{message["content"]}</div>
                <button class="share-btn" onclick="shareContent('{clean_text}')" title="Share">🔗</button>
            </div>
            """, unsafe_allow_html=True)

    # चैट इनपुट बॉक्स
    if user_message := st.chat_input("यहाँ अपना सवाल लिखें..."):
        st.markdown(f'<div class="user-msg-container"><div class="user-msg">🧑 <b>You:</b><br>{user_message}</div></div>', unsafe_allow_html=True)
        st.session_state.messages.append({"role": "user", "content": user_message})

        try:
            bot_reply = ""
            current_ai = st.session_state.saved_ai
            current_key = st.session_state.saved_key
            
            master_prompt = f"You are the digital twin of the user. Replicate their style based on this: {st.session_state.twin_personality}. User Message: {user_message}"
            
            if current_ai == "Google Gemini":
                genai.configure(api_key=current_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                response = model.generate_content(master_prompt)
                bot_reply = response.text
            
            elif current_ai == "Groq (Llama 3 - FREE)":
                client = Groq(api_key=current_key)
                completion = client.chat.completions.create(
                    model="llama3-8b-8192",
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
            st.error(f"एरर आया! एरर: {e}")
            
