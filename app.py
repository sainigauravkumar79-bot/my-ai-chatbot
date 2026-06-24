import streamlit as st

st.set_page_config(
    page_title="Gaurav AI Twin",
    page_icon="🤖"
)

st.title("🤖 Gaurav AI Twin")
st.write("Welcome to your AI Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_input = st.chat_input("Type your message...")

if user_input:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    with st.chat_message("user"):
        st.write(user_input)

    # Temporary AI Reply
    bot_reply = f"Hello Gaurav 👋, you said: {user_input}"

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": bot_reply
        }
    )

    with st.chat_message("assistant"):
        st.write(bot_reply)
