import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from anthropic import Anthropic

st.title("Chatbot Interviewer")
st.write("This chatbot will interview you and generate a compelling story based on your responses.")

# Anthropic API key (stored as a Streamlit secret)
anthropic_api_key = st.secrets["ANTHROPIC_API_KEY"]

# Email credentials (stored as Streamlit secrets)
email_user = st.secrets["EMAIL_USER"]
email_password = st.secrets["EMAIL_PASSWORD"]
email_server = st.secrets["EMAIL_SERVER"]
email_port = st.secrets["EMAIL_PORT"]

# Initialize Anthropic client
client = Anthropic(api_key=anthropic_api_key)

# Initialize session state with an initial message
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm here to interview you. Let's start!"}
    ]

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What would you like to share?"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        # Stream the response from Anthropic API
        stream = client.messages.stream(
            model="claude-3-opus-20240229",
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            max_tokens=1000,
            temperature=1,
        )

        # Display the streamed response
        response_text = ""
        for data in stream:
            response_text += data.content
            st.markdown(response_text)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response_text})

# Function to send email with transcript and generated story
def send_email(transcript, story, recipient):
    msg = MIMEMultipart()
    msg["From"] = email_user
    msg["To"] = recipient
    msg["Subject"] = "Chatbot Interview Transcript and Story"
    msg.attach(MIMEText(f"Interview Transcript:\n\n{transcript}\n\nGenerated Story:\n\n{story}"))
    server = smtplib.SMTP(email_server, email_port)
    server.starttls()
    server.login(email_user, email_password)
    server.send_message(msg)
    server.quit()