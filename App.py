import streamlit as st
import openai

# ऐप का टाइटल और डिज़ाइन
st.set_page_config(page_title="Gaurav's AI Chatbot", page_icon="🤖")
st.title("🤖 Gaurav's Custom AI Chatbot")
st.write("अपना OpenAI API Key डालिए और चैटबॉट का मज़ा लीजिए!")

# 1. यूजर से उसकी API Key लेना
user_api_key = st.text_input("अपनी OpenAI API Key यहाँ पेस्ट करें:", type="password")

# 2. चैट हिस्ट्री (मैसेज याद रखने के लिए)
if "messages" not in st.session_state:
    st.session_state.messages = []

# पुरानी चैट स्क्रीन पर दिखाना
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 3. यूजर का इनपुट बॉक्स (सवाल पूछने के लिए)
if user_message := st.chat_input("यहाँ अपना सवाल लिखें..."):
    
    # अगर यूजर ने API Key नहीं डाली है
    if not user_api_key:
        st.error("कृपया पहले ऊपर अपनी OpenAI API Key डालें!")
    else:
        # यूजर का मैसेज स्क्रीन पर दिखाना और सेव करना
        st.chat_message("user").markdown(user_message)
        st.session_state.messages.append({"role": "user", "content": user_message})

        try:
            # यूजर की API Key का इस्तेमाल करके OpenAI को कनेक्ट करना
            client = openai.OpenAI(api_key=user_api_key)
            
            # AI से जवाब मांगना
            response = client.chat.completions.create(
                model="gpt-3.5-turbo", # आप यहाँ gpt-4o-mini भी रख सकते हैं
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ]
            )
            
            # AI का जवाब स्क्रीन पर दिखाना
            bot_reply = response.choices[0].message.content
            with st.chat_message("assistant"):
                st.markdown(bot_reply)
            
            # जवाब को हिस्ट्री में सेव करना
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            
        except Exception as e:
            st.error(f"कुछ गड़बड़ हुई! चेक करें कि आपकी API Key सही है या नहीं। एरर: {e}")
          
