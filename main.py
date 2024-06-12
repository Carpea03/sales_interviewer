import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from openai import OpenAI
import tornado.websocket

# Function to send email with transcript and generated story
def send_email(transcript, story, recipient):
    try:
        yag = yagmail.SMTP(email_user, email_password)
        subject = "Sales Interview Transcript"
        content = f"Interview Transcript:\n\n{transcript}\n\nGenerated Content:\n\n{story}"
        yag.send(to=recipient, subject=subject, contents=content)
        return True
    except Exception as e:
        st.error(f"An error occurred while sending the email: {str(e)}")
        return False

st.title("Sales Interviewer")
st.write(
    "This chatbot will interview you and generate content based on your responses."
)

# OpenAI API key and email credentials (stored as Streamlit secrets)
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
email_user = st.secrets["EMAIL_USER"]
email_password = st.secrets["EMAIL_PASSWORD"]
email_server = st.secrets["EMAIL_SERVER"]
email_port = st.secrets["EMAIL_PORT"]

# Validate static values immediately after they're defined
assert isinstance(OPENAI_API_KEY, str), "API key must be a string"
assert isinstance(email_user, str), "Email user must be a string"
# Assertions for email_password, email_server, and email_port could be added here as needed

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Initialize 'conversation_history' in session_state if it doesn't exist
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = [
        {"role": "user", "content": "Hi"},
        {
            "role": "assistant",
            "content": "Hello! I'm an AI interviewer can you tell me which clients you'd like to talk about today?",
        },
    ]

# Display chat messages from history on app rerun
for message in st.session_state.conversation_history[1:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
prompt = st.chat_input(
    "What would you like to share?",
    disabled=st.session_state.conversation_history[-1]["role"] == "user",
)
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
        response = client.chat_completion(
            model="gpt-4o",
            max_tokens=4096,
            temperature=1,
            system_message="""
            Your task is to engage in a conversation with a sales professional and interview them about their experience
            """,
            messages=st.session_state.conversation_history,
        )
        response_text = response['choices'][0]['message']['content']
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.stop()

    # Add assistant response to conversation history
    st.session_state.conversation_history.append({"role": "assistant", "content": response_text})

    # Display assistant response in chat message container
    try:
        with st.chat_message("assistant"):
            st.markdown(response_text)
    except tornado.websocket.WebSocketClosedError:
        st.warning("The connection was closed unexpectedly. Please refresh the page and try again.")
        st.stop()

    # Extract the article from the response
    if "<article>" in response_text:
        article_start = response_text.index("<article>") + len("<article>")
        article_end = response_text.index("</article>")
        article = response_text[article_start:article_end].strip()

        # Generate the interview transcript
        transcript = "\n".join([f"{message['role']}: {message['content']}" for message in st.session_state.conversation_history])

        # Send the email with the transcript and article
        email_sender = st.secrets["EMAIL_USER"]
        email_receiver = "alexcarpenter2000@gmail.com"
        subject = "Sales Interview Transcript"
        body = f"Interview Transcript:\n\n{transcript}\n\nGenerated Content:\n\n{article}"
        password = st.secrets["EMAIL_PASSWORD"]

        try:
            msg = MIMEMultipart()
            msg['From'] = email_sender
            msg['To'] = email_receiver
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(email_sender, password)
            server.send_message(msg)
            server.quit()

            st.success('Thank you so much for taking the time to have a conversation')
        except Exception as e:
            st.error(f"An error occurred while sending the email: {e}")

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.stop()
