import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from anthropic import Anthropic
import tornado.websocket
import os
from datetime import datetime
import uuid
import logging

import re

def strip_xml_tags(text):
    # Remove <response> and </response> tags
    text = re.sub(r'</?response>', '', text)
    # Remove <insights_summary> and </insights_summary> tags
    text = re.sub(r'</?insights_summary>', '', text)
    return text.strip()

# Function to send email with transcript and generated story
def send_email(transcript, story, recipient):
    sender = email_user
    password = email_password
    subject = "Sales Interview Transcript"
    content = f"Interview Transcript:\n\n{transcript}"

    try:
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = recipient
        msg['Subject'] = subject
        
        msg.attach(MIMEText(content, 'plain'))
        
        with smtplib.SMTP(email_server, email_port) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"An error occurred while sending the email: {str(e)}")
        return False

# Set up logging
logging.basicConfig(filename='chatbot.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Create a directory for conversation files if it doesn't exist
CONVERSATION_DIR = "conversations"
os.makedirs(CONVERSATION_DIR, exist_ok=True)

# Function to save new messages to the current conversation file
def save_conversation(new_messages, conversation_id):
    filename = os.path.join(CONVERSATION_DIR, f"conversation_{conversation_id}.txt")
    try:
        with open(filename, "a") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if os.path.getsize(filename) == 0:
                f.write(f"Conversation started at {timestamp}\n\n")
                logging.info(f"New conversation file created: {filename}")
            else:
                f.write(f"\n--- New messages at {timestamp} ---\n")
            for message in new_messages:
                f.write(f"{message['role']}: {message['content']}\n")
        logging.info(f"Conversation updated: {filename}")
    except IOError as e:
        error_msg = f"IOError occurred while saving the conversation: {str(e)}"
        logging.error(error_msg)
        st.error(error_msg)
    except Exception as e:
        error_msg = f"An unexpected error occurred while saving the conversation: {str(e)}"
        logging.error(error_msg)
        st.error(error_msg)

def end_conversation():
    """Handle the end of the conversation, including sending the email."""
    logging.info(f"Attempting to end conversation for ID: {st.session_state.conversation_id}")
    
    transcript = "\n".join([f"{message['role']}: {message['content']}" for message in st.session_state.conversation_history])
    
    email_sender = st.secrets["EMAIL_USER"]
    email_receiver = "alexcarpenter2000@gmail.com"
    subject = "Sales Interview Transcript"
    body = f"Interview Transcript:\n\n{transcript}"
    
    try:
        send_email(transcript, "", email_receiver)
        st.success('Thank you for the conversation. The transcript has been sent via email.')
        # Reset the conversation
        logging.info(f"Conversation ended and email sent for conversation ID: {st.session_state.conversation_id}")
        st.session_state.conversation_history = []
        st.session_state.conversation_id = str(uuid.uuid4())
    except Exception as e:
        st.error(f"An error occurred while ending the conversation: {e}")
        error_msg = f"An error occurred while ending the conversation: {str(e)}"
        logging.error(error_msg)
        st.error(error_msg)
st.title("Sales Interviewer")
st.write(
    "This chatbot will interview you and generate content based on your responses."
)

# Anthropic API key and email credentials (stored as Streamlit secrets)
ANTHROPIC_API_KEY = st.secrets["ANTHROPIC_API_KEY"]
email_user = st.secrets["EMAIL_USER"]
email_password = st.secrets["EMAIL_PASSWORD"]
email_server = st.secrets["EMAIL_SERVER"]
email_port = st.secrets["EMAIL_PORT"]

# Validate static values immediately after they're defined
assert isinstance(ANTHROPIC_API_KEY, str), "API key must be a string"
assert isinstance(email_user, str), "Email user must be a string"
assert isinstance(email_password, str), "Email password must be a string"
assert isinstance(email_server, str), "Email server must be a string"
assert isinstance(email_port, int), "Email port must be an integer"

# Initialize Anthropic client
client = Anthropic(api_key=ANTHROPIC_API_KEY)

# Initialize conversation ID in session state if it doesn't exist
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = str(uuid.uuid4())

# Initialize 'conversation_history' in session_state if it doesn't exist
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = [
        {"role": "user", "content": "Hi"},
        {
            "role": "assistant",
            "content": "Hello! It's great to meet you. I'm an AI assistant here to conduct an interview about your experiences as a sales professional. I'm looking forward to learning from you and gathering insights that could be helpful for other salespeople. To start off, could you tell me a bit about the organization or organizations you currently sell for?",
        },
    ]

# Display chat messages from history on app rerun
for message in st.session_state.conversation_history[1:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Add "End Conversation" button
if st.button("End Conversation"):
    end_conversation()

# Initialize the conversation history if it doesn't exist
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

# Check if the conversation history is not empty before accessing the last item
if st.session_state.conversation_history:
    disabled = st.session_state.conversation_history[-1]["role"] == "user"
else:
    disabled = False

# Accept user input
prompt = st.chat_input(
    "What would you like to share?",
    disabled=disabled
)
if prompt:
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Add user message to conversation history
    st.session_state.conversation_history.append({"role": "user", "content": prompt})
    save_conversation([{"role": "user", "content": prompt}], st.session_state.conversation_id)

    # Generate assistant response only if the last message in the conversation history is from the user
if st.session_state.conversation_history[-1]["role"] == "user":
    response_text = ""
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=4096,
            temperature=1,
            system="""
            You are an AI assistant tasked with conducting an interview with a sales professional to extract useful and actionable insights for other salespeople. Your goal is to engage in a natural conversation while gathering specific information about their experiences and practices.

Here is the conversation history so far:
<conversation_history>
{{CONVERSATION_HISTORY}}
</conversation_history>

The current question to ask or respond to is:
<current_question>
{{CURRENT_QUESTION}}
</current_question>

Follow these guidelines when conducting the interview:

1. Start with introductory questions to build rapport and gather basic information:
   - What organizations do you sell for?
   - What is your working arrangement (Full time? Contractor?)
   - What are your average deal sizes?
   - What segment of the market do you sell into?
   - Where are you based?

2. Gradually transition to more in-depth questions about their selling experiences:
   - Ask them to share a recent selling experience, both positive and negative.
   - Inquire about specific organizations they've sold to.
   - Ask about stakeholders and their behavior.
   - Request advice for other sales representatives.

3. Be sure to ask about their interest in a platform that provides reviews on the companies they sell to.

4. Maintain a conversational tone throughout the interview. Avoid asking all questions at once; instead, ask one or two questions at a time and wait for the interviewee's response.

5. Listen actively to the interviewee's responses and ask relevant follow-up questions based on the information they provide. This will help you gather more detailed and valuable insights.

6. If the interviewee mentions something interesting or unique about their sales approach or experience, probe deeper to understand the context and potential lessons for other salespeople.

7. Throughout the conversation, mentally note key insights, strategies, or advice that could be valuable for other sales professionals.

8. After gathering sufficient information, summarize the key insights and actionable advice extracted from the interview.

When responding to the current question or asking a new question, format your response as follows:

<response>
[Your response to the current question or your next question for the interviewee]
</response>

Remember to maintain a friendly and professional tone throughout the interview, and adapt your questions based on the flow of the conversation and the information provided by the interviewee.
            """,
            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.conversation_history],
        )
        response_text = response.content[0].text
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.stop()

    # Add assistant response to conversation history
    st.session_state.conversation_history.append({"role": "assistant", "content": response_text})
    save_conversation([{"role": "assistant", "content": response_text}], st.session_state.conversation_id)

    # Strip XML tags from the response
    cleaned_response = strip_xml_tags(response_text)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(cleaned_response)

    # Update the conversation history with the cleaned response
    st.session_state.conversation_history[-1]["content"] = cleaned_response
