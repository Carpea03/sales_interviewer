import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from anthropic import Anthropic

st.title("Chatbot Interviewer")
st.write("This chatbot will interview you and generate a compelling story based on your responses.")

# Anthropic API key and email credentials (stored as Streamlit secrets)
anthropic_api_key = st.secrets["ANTHROPIC_API_KEY"]
email_user = st.secrets["EMAIL_USER"]
email_password = st.secrets["EMAIL_PASSWORD"]
email_server = st.secrets["EMAIL_SERVER"]
email_port = st.secrets["EMAIL_PORT"]

# Validate static values immediately after they're defined
assert isinstance(anthropic_api_key, str), "API key must be a string"
assert isinstance(email_user, str), "Email user must be a string"
# Assertions for email_password, email_server, and email_port could be added here as needed

# Initialize Anthropic client
client = Anthropic(api_key=anthropic_api_key)

# Initialize 'conversation_history' in session_state if it doesn't exist
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = [
        {"role": "user", "content": "Hello! I'm here to be interviewed. Please ask me some questions."}
    ]

# Display chat messages from history on app rerun
for message in st.session_state.conversation_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
prompt = st.chat_input("What would you like to share?",disabled=st.session_state.conversation_history[-1]["role"] == "user")
if prompt:
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Add user message to conversation history
    st.session_state.conversation_history.append({"role": "user", "content": prompt})

    # Generate assistant response only if the last message in the conversation history is from the user
if st.session_state.conversation_history[-1]["role"] == "user":
    response_text = ""
    try:
        with client.messages.stream(
            model="claude-3-opus-20240229",
            max_tokens=1000,
            temperature=1,
            messages=st.session_state.conversation_history,
        ) as stream:
            for text in stream.text_stream:
                response_text += text
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

    # Add assistant response to conversation history
    st.session_state.conversation_history.append({"role": "assistant", "content": response_text})

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response_text)

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