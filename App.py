import streamlit as st
import google.generativeai as genai
from groq import Groq
import openai
import urllib.parse

st.set_page_config(page_title="MIRROR AI - Your Digital Twin", page_icon="🧠", layout="wide")

# --- 1. प्रीमियम चैट और बटन स्टाइल (CSS Style) ---
st.markdown("""
<style>
    .user-msg-container { display: flex; justify-content: flex-end; margin-bottom: 15px; }
    .user-msg { 
        background: linear-gradient(135deg, #00c6ff, #0072ff); 
        color: white; padding: 12px 18px; border-radius: 20px 20px 0px 20px; 
        max-width: 70%; font-family: 'Helvetica Neue', sans-serif; box-shadow: 0px 4px 10px rgba(0,114,255,0.3);
    }
    .twin-msg-container { display: flex; justify-content: flex-start; margin-bottom: 15px; }
    .twin-msg { 
        background: linear-gradient(135deg, #3a3d40, #181717); 
        color: #f5f5f5; padding: 12px 18px; border-radius: 20px 20px 20px 0px; 
        max-width: 70%; font-family: 'Helvetica Neue', sans-serif; border: 1px solid #444; box-shadow: 0px 4px 10px rgba(0,0,0,0.5);
    }
</style>
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

# --- 3. पहला पेज: MIRROR AI एडवांस्ड ट्रेनिंग और सेटअप ---
if not st.session_state.keys_saved:
    st.title("🧠 MIRROR AI: Personal Digital Twin")
    st.subheader("अपनी एआई चाबी डालें और अपने डिजिटल जुड़वां को एडवांस ट्रेन करें")
    st.write("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔑 स्टेप 1: इंफ्रास्ट्रक्चर लिंक करें")
        ai_choice = st.selectbox(
            "अपना पसंदीदा AI इंजन चुनें:",
            ("Google Gemini", "Groq (Llama 3 - FREE)", "OpenAI (ChatGPT)")
        )
        key_input = st.text_input(f"अपनी {ai_choice} API Key यहाँ पेस्ट करें:", type="password")
        
    with col2:
        st.markdown("### 📝 स्टेप 2: अपने जुड़वां (Twin) को ट्रेन करें")
        personality_input = st.text_area(
            "एआई को अपने बारे में लिखकर बताएं:",
            placeholder="जैसे: मेरा नाम गौरव है। मैं दोस्तों से 'भाई' करके बात करता हूँ...",
            height=80
        )
        
        # New Feature: फ़ाइल अपलोडर (मेमोरी मेश)
        uploaded_file = st.file_uploader("🧠 या अपनी पुरानी चैट्स/डायरी की TXT फ़ाइल अपलोड करें (ऑप्शनल):", type=["txt"])
        file_context = ""
        if uploaded_file is not None:
            file_context = "\nADDITIONAL UPLOADED TRAINING DATA:\n" + str(uploaded_file.read().decode("utf-8"))
            st.success("ट्रेनिंग फ़ाइल सफलतापूर्वक लोड हो गई!")
        
    st.write("---")
    if st.button("🔥 ACTIVATE MY DIGITAL TWIN 🚀", use_container_width=True):
        if not key_input:
            st.error("आगे बढ़ने के लिए API Key डालना अनिवार्य है!")
        elif not personality_input and not file_context:
            st.error("अपने ट्विन को एक्टिवेट करने के लिए लिखकर बताएं या कोई फ़ाइल अपलोड करें!")
        else:
            st.session_state.saved_ai = ai_choice
            st.session_state.saved_key = key_input
            # दोनों टेक्स्ट और फ़ाइल डेटा को मिलाकर मास्टर पर्सनैलिटी बनाना
            st.session_state.twin_personality = personality_input + file_context
            st.query_params["page"] = "chat"
            st.rerun()

# --- 4. दूसरा पेज: MIRROR AI ADVANCED CHAT ROOM ---
else:
    with st.sidebar:
        st.header("🧠 Mirror Core Status")
        st.success(f"🟢 {st.session_state.saved_ai} Active")
        st.info("💡 आपका ट्विन पूरी तरह सिंक हो चुका है और एक्शन लेने के लिए तैयार है।")
        st.write("---")
        if st.button("🔄 री-ट्रेन करें / लॉगआउट"):
            st.query_params.clear()
            st.rerun()
        st.write("👉 अपने **फ़ोन का बैक बटन** दबाकर भी आप ट्रेनिंग पेज पर वापस जा सकते हैं।")

    st.title("👥 Your Digital Twin Chatroom")
    st.write("---")

    # चैट हिस्ट्री दिखाना (व्हाट्सएप शेयर फीचर के साथ)
    for index, message in enumerate(st.session_state.messages):
        if message["role"] == "user":
            st.markdown(f'<div class="user-msg-container"><div class="user-msg">🧑 <b>You:</b><br>{message["content"]}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="twin-msg-container"><div class="twin-msg">🧠 <b>Mirror Twin:</b><br>{message["content"]}</div></div>', unsafe_allow_html=True)
            
            # New Feature: प्रत्येक रिप्लाई के नीचे व्हाट्सएप शेयर बटन
            encoded_reply = urllib.parse.quote(message["content"])
            whatsapp_url = f"https://wa.me/?text={encoded_reply}"
            st.markdown(f'<a href="{whatsapp_url}" target="_blank" style="text-decoration:none;"><button style="background-color:#25D366; color:white; border:none; padding:5px 10px; border-radius:10px; cursor:pointer; font-size:12px; margin-bottom:15px;">📲 Share on WhatsApp</button></a>', unsafe_allow_html=True)

    # चैट इनपुट बॉक्स
    if user_message := st.chat_input("अपने डिजिटल ट्विन को कोई मैसेज ड्राफ्ट करने को कहें..."):
        st.markdown(f'<div class="user-msg-container"><div class="user-msg">🧑 <b>You:</b><br>{user_message}</div></div>', unsafe_allow_html=True)
        st.session_state.messages.append({"role": "user", "content": user_message})

        try:
            bot_reply = ""
            current_ai = st.session_state.saved_ai
            current_key = st.session_state.saved_key
            
            master_prompt = f"""
            You are the digital twin (clone) of the user. Replicate their personality based on this data:
            {st.session_state.twin_personality}
            
            Respond exactly in their tone and style.
            User Message: {user_message}
            """
            
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
            st.error(f"मिरर कोर एरर! विवरण: {e}")
