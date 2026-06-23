import streamlit as st
import openai
import google.generativeai as genai
from groq import Groq

st.set_page_config(page_title="Gaurav's Multi-AI Chatbot", page_icon="🤖")

# --- 1. मेमोरी (Session State) सेट करना ---
if "saved_ai" not in st.session_state:
    st.session_state.saved_ai = "Google Gemini"
if "saved_key" not in st.session_state:
    st.session_state.saved_key = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 2. ब्राउज़र URL / फ़ोन बैक बटन सपोर्ट ---
query_params = st.query_params

if "page" not in query_params:
    st.session_state.keys_saved = False
elif query_params["page"] == "chat":
    st.session_state.keys_saved = True

# --- 3. पहला पेज: SIMPLE SETUP PAGE ---
if not st.session_state.keys_saved:
    st.title("🔑 Gaurav's AI Setup")
    st.write("चैट शुरू करने से पहले अपना AI और API Key सेट करें।")
    
    # सिर्फ 2 ही ऑप्शन बॉक्स (जैसा आप चाहते थे!)
    ai_choice = st.selectbox(
        "कौन सा AI इस्तेमाल करना चाहते हैं?",
        ("Google Gemini", "Groq (Llama 3 - FREE)", "OpenAI (ChatGPT)")
    )
    
    key_input = st.text_input(f"अपनी {ai_choice} API Key यहाँ पेस्ट करें:", type="password")
    
    # OK BUTTON
    if st.button("OK - Save & Start Chatting 🚀", use_container_width=True):
        if not key_input:
            st.error(f"कृपया आगे बढ़ने के लिए {ai_choice} की API Key ज़रूर डालें!")
        else:
            # चुनी हुई चाबी और मॉडल मेमोरी में सेव करना
            st.session_state.saved_ai = ai_choice
            st.session_state.saved_key = key_input
            
            # यूआरएल में '?page=chat' जोड़ना (ताकि फ़ोन का बैक बटन काम करे)
            st.query_params["page"] = "chat"
            st.rerun()

# --- 4. दूसरा पेज: NEW CHAT PAGE ---
else:
    with st.sidebar:
        st.header("⚙️ Settings")
        st.write(f"🤖 **Active AI:** {st.session_state.saved_ai}")
        st.write("---")
        if st.button("🔄 Change AI / Reset"):
            st.query_params.clear()  # यूआरएल साफ़ करके वापस सेटअप पेज पर भेजेगा
            st.rerun()
        st.write("💡 **टिप:** आप अपने **फ़ोन का बैक बटन** दबाकर भी वापस जा सकते हैं!")

    st.title(f"🤖 Gaurav's {st.session_state.saved_ai} Chat")
    
    # पुरानी चैट हिस्ट्री दिखाना
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # चैट इनपुट बॉक्स
    if user_message := st.chat_input("यहाँ अपना सवाल लिखें..."):
        st.chat_message("user").markdown(user_message)
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

            with st.chat_message("assistant"):
                st.markdown(bot_reply)
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            st.rerun()
            
        except Exception as e:
            st.error(f"एरर आया! कृपया चेक करें कि की (Key) सही है या नहीं। एरर: {e}")
            
