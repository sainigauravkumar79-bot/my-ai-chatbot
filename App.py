import streamlit as st
import openai
import google.generativeai as genai
from groq import Groq

st.set_page_config(page_title="Gaurav's Multi-AI Chatbot", page_icon="🤖")

# --- 1. मेमोरी (Session State) सेट करना ---
if "gemini_key" not in st.session_state:
    st.session_state.gemini_key = ""
if "groq_key" not in st.session_state:
    st.session_state.groq_key = ""
if "openai_key" not in st.session_state:
    st.session_state.openai_key = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 2. ब्राउज़र URL / फ़ोन बैक बटन का जुगाड़ ---
# यूआरएल से चेक करना कि हम किस पेज पर हैं
query_params = st.query_params

if "page" not in query_params:
    # अगर यूआरएल में कुछ नहीं है, तो डिफ़ॉल्ट रूप से सेटअप पेज
    st.session_state.keys_saved = False
elif query_params["page"] == "chat":
    st.session_state.keys_saved = True

# --- 3. पहला पेज: API KEYS SETUP PAGE ---
if not st.session_state.keys_saved:
    st.title("🔑 Gaurav's AI Setup")
    st.write("चैट शुरू करने से पहले अपनी API Keys यहाँ सेट करें।")
    
    # चाबियाँ इनपुट करने के बॉक्स
    gemini_input = st.text_input("Google Gemini Key (Optional):", value=st.session_state.gemini_key, type="password")
    groq_input = st.text_input("Groq Key (Optional):", value=st.session_state.groq_key, type="password")
    openai_input = st.text_input("OpenAI Key (Optional):", value=st.session_state.openai_key, type="password")
    
    # OK BUTTON
    if st.button("OK - Save Keys & Start Chatting 🚀", use_container_width=True):
        if not gemini_input and not groq_input and not openai_input:
            st.error("कृपया आगे बढ़ने के लिए कम से कम कोई एक API Key ज़रूर डालें!")
        else:
            # चाबियों को मेमोरी में सेव करना
            st.session_state.gemini_key = gemini_input
            st.session_state.groq_key = groq_input
            st.session_state.openai_key = openai_input
            
            # यूआरएल में '?page=chat' जोड़ना (ताकि फ़ोन का बैक बटन काम करे)
            st.query_params["page"] = "chat"
            st.rerun()

# --- 4. दूसरा पेज: NEW CHAT PAGE ---
else:
    with st.sidebar:
        st.header("⚙️ Settings")
        # स्क्रीन वाले बटन से भी वापस जाने का विकल्प
        if st.button("🔄 Change API Keys / Logout"):
            st.query_params.clear()  # यूआरएल साफ़ करेगा, जिससे फ़ोन बैक जैसा इफ़ेक्ट आएगा
            st.rerun()
        st.write("---")
        st.write("💡 **टिप:** अब आप अपने **फ़ोन का बैक बटन** दबाकर भी वापस सेटअप पेज पर जा सकते हैं!")

    st.title("🤖 Gaurav's Chat Room")
    
    ai_option = st.selectbox(
        "कौन सा AI इस्तेमाल करना चाहते हैं?",
        ("Google Gemini", "Groq (Llama 3 - FREE)", "OpenAI (ChatGPT)")
    )

    current_api_key = ""
    if ai_option == "Google Gemini":
        current_api_key = st.session_state.gemini_key
    elif ai_option == "Groq (Llama 3 - FREE)":
        current_api_key = st.session_state.groq_key
    elif ai_option == "OpenAI (ChatGPT)":
        current_api_key = st.session_state.openai_key

    # चैट हिस्ट्री दिखाना
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # चैट इनपुट बॉक्स
    if user_message := st.chat_input("यहाँ अपना सवाल लिखें..."):
        if not current_api_key:
            st.error(f"आपने सेटअप पेज पर {ai_option} की Key नहीं डाली थी!")
        else:
            st.chat_message("user").markdown(user_message)
            st.session_state.messages.append({"role": "user", "content": user_message})

            try:
                bot_reply = ""
                
                if ai_option == "Google Gemini":
                    genai.configure(api_key=current_api_key)
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    response = model.generate_content(user_message)
                    bot_reply = response.text
                
                elif ai_option == "Groq (Llama 3 - FREE)":
                    client = Groq(api_key=current_api_key)
                    completion = client.chat.completions.create(
                        model="llama3-8b-8192",
                        messages=[{"role": "user", "content": user_message}]
                    )
                    bot_reply = completion.choices[0].message.content
                
                elif ai_option == "OpenAI (ChatGPT)":
                    client = openai.OpenAI(api_key=current_api_key)
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
                st.error(f"एरर आया! एरर: {e}")
                
