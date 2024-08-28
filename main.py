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
import json
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import re
import pymongo

# Load secrets at the beginning of the script
try:
    ANTHROPIC_API_KEY = st.secrets["ANTHROPIC_API_KEY"]
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY is empty")
    email_user = st.secrets["EMAIL_USER"]
    email_password = st.secrets["EMAIL_PASSWORD"]
    email_server = st.secrets["EMAIL_SERVER"]
    email_port = st.secrets["EMAIL_PORT"]
except KeyError as e:
    st.error(f"Missing required secret: {e}")
    logging.error(f"Missing required secret: {e}")
    st.stop()
except ValueError as e:
    st.error(str(e))
    logging.error(str(e))
    st.stop()
except Exception as e:
    st.error(f"An error occurred while accessing secrets: {e}")
    logging.error(f"Error accessing secrets: {e}", exc_info=True)
    st.stop()

# Anthropic client is now initialized at the beginning of the script

def strip_xml_tags(text):
    if isinstance(text, list):
        text = ' '.join(text)  # Join list elements into a single string
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
    try:
        timestamp = datetime.now().isoformat()
        conversation_data = conversations.find_one({"conversation_id": conversation_id})
        
        if not conversation_data:
            conversation_data = {"conversation_id": conversation_id, "messages": []}
            logging.info(f"New conversation created: {conversation_id}")
        
        for message in new_messages:
            conversation_data["messages"].append({
                "timestamp": timestamp,
                "role": message["role"],
                "content": message["content"]
            })
        
        conversations.update_one(
            {"conversation_id": conversation_id},
            {"$set": conversation_data},
            upsert=True
        )
        logging.info(f"Conversation updated: {conversation_id}")
    except Exception as e:
        error_msg = f"An unexpected error occurred while saving the conversation: {str(e)}"
        logging.error(error_msg)
        st.error(error_msg)

def end_conversation():
    """Handle the end of the conversation, including sending the email."""
    logging.info(f"Attempting to end conversation for ID: {st.session_state.conversation_id}")
    
    transcript = "\n".join([f"{message['role']}: {message['content']}" for message in st.session_state.conversation_history])
    
    email_sender = st.secrets["EMAIL_USER"]
    email_receiver = "alexcarpenter2000@gmail.com , palacios.david88@gmail.com"
    subject = "Sales Interview Transcript"
    body = f"Interview Transcript:\n\n{transcript}"
    
    try:
        send_email(transcript, "", email_receiver)
        st.success('Thank you for the conversation. Have a great day!')
        # Reset the conversation
        logging.info(f"Conversation ended and email sent for conversation ID: {st.session_state.conversation_id}")
        st.session_state.conversation_history = []
        st.session_state.conversation_id = str(uuid.uuid4())
    except Exception as e:
        st.error(f"An error occurred while ending the conversation: {e}")
        error_msg = f"An error occurred while ending the conversation: {str(e)}"
        logging.error(error_msg)
        st.error(error_msg)
import streamlit.components.v1 as components

# Function to read HTML content
def read_html_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

# Set up the main layout and theme
st.set_page_config(
    page_title="Sales Interviewer Chatbot",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply custom theme
st.markdown("""
<style>
:root {
    --primary-color: #3498db;
    --secondary-color: #2ecc71;
    --background-color: #f0f0f0;
    --text-color: #333333;
}
body {
    color: var(--text-color);
    background-color: var(--background-color);
}
.stButton>button {
    color: white;
    background-color: var(--primary-color);
    border-radius: 5px;
}
.stTextInput>div>div>input {
    border-color: var(--primary-color);
}
</style>
""", unsafe_allow_html=True)

# Create a sidebar
with st.sidebar:
    st.title("Sales Interviewer Chatbot")
    st.write("Welcome to the Sales Interviewer Chatbot. This AI-powered tool will conduct an interview to gather insights about your sales experiences.")

# Main content area
if 'interview_started' not in st.session_state:
    st.session_state.interview_started = False

if not st.session_state.interview_started:
    # Display the landing page
    col1, col2 = st.columns([2, 1])
    with col1:
        landing_page_html = read_html_file('landing_page.html')
        components.html(landing_page_html, height=400)
    with col2:
        st.header("Ready to start?")
        if st.button("Start Interview", key="start_interview", use_container_width=True):
            st.session_state.interview_started = True
            st.experimental_rerun()
else:
    # Chat interface
    st.markdown("""
    <style>
    .chat-container {
        height: 70vh;
        overflow-y: auto;
        display: flex;
        flex-direction: column-reverse;
        border: 1px solid #ddd;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 80px;
    }
    .user-message {
        background-color: var(--primary-color);
        color: white;
        padding: 10px;
        border-radius: 15px;
        margin: 5px 0;
    }
    .assistant-message {
        background-color: var(--secondary-color);
        color: white;
        padding: 10px;
        border-radius: 15px;
        margin: 5px 0;
    }
    .input-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        padding: 10px;
        background-color: white;
        box-shadow: 0 -2px 5px rgba(0,0,0,0.1);
    }
    </style>
    <div class="chat-container" id="chat-container">
    """, unsafe_allow_html=True)
    
    # Display chat messages
    for message in reversed(st.session_state.conversation_history[1:]):
        st.markdown(f"<div class='{message['role']}-message'>{message['content']}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Input area and end conversation button
    st.markdown("""<div class="input-container">""", unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1:
        prompt = st.text_input("Your response:", key="chat_input")
    with col2:
        if st.button("End Conversation", key="end_conversation"):
            end_conversation()
            st.session_state.interview_started = False
            st.experimental_rerun()
    st.markdown("""</div>""", unsafe_allow_html=True)
    
    # Automatically scroll to the bottom of the chat container
    st.markdown("""
    <script>
        var chatContainer = document.getElementById('chat-container');
        chatContainer.scrollTop = chatContainer.scrollHeight;
    </script>
    """, unsafe_allow_html=True)
    
    # Chat input and end conversation button are now handled in the markdown above
    # Anthropic API key and email credentials (stored as Streamlit secrets)
    try:
        ANTHROPIC_API_KEY = st.secrets["ANTHROPIC_API_KEY"]
        if not ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is empty")
        email_user = st.secrets["EMAIL_USER"]
        email_password = st.secrets["EMAIL_PASSWORD"]
        email_server = st.secrets["EMAIL_SERVER"]
        email_port = st.secrets["EMAIL_PORT"]
    except KeyError as e:
        st.error(f"Missing required secret: {e}")
        logging.error(f"Missing required secret: {e}")
        st.stop()
    except ValueError as e:
        st.error(str(e))
        logging.error(str(e))
        st.stop()
    except Exception as e:
        st.error(f"An error occurred while accessing secrets: {e}")
        logging.error(f"Error accessing secrets: {e}", exc_info=True)
        st.stop()

try:
    # Check if MongoClient is in the global namespace
    if 'MongoClient' not in globals():
        st.error("MongoClient is not in the global namespace")
        raise NameError("MongoClient is not defined")

    # Proceed with the connection attempt
    mongo_uri = st.secrets["mongo"]["uri"]
    
    client = MongoClient(mongo_uri)
    
    db = client.sales_interviewer
    conversations = db.conversations
    
    client.admin.command('ping')
    
    logging.info("Successfully connected to MongoDB Atlas")
except KeyError as e:
    error_msg = f"Failed to retrieve MongoDB URI from secrets: {e}"
    st.error(error_msg)
    logging.error(error_msg, exc_info=True)
except AttributeError as e:
    error_msg = f"AttributeError occurred (possibly due to pymongo import issue): {e}"
    st.error(error_msg)
    logging.error(error_msg, exc_info=True)
except pymongo.errors.ConnectionFailure as e:
    error_msg = f"Failed to connect to MongoDB Atlas: {e}"
    st.error(error_msg)
    logging.error(error_msg, exc_info=True)
except NameError as e:
    error_msg = f"NameError occurred: {e}"
    st.error(error_msg)
    logging.error(error_msg, exc_info=True)
except Exception as e:
    error_msg = f"An unexpected error occurred: {e}"
    st.error(error_msg)
    st.write(f"Error type: {type(e).__name__}")
    logging.error(error_msg, exc_info=True)

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
if 'interview_started' in st.session_state and st.session_state.interview_started:
    for message in st.session_state.conversation_history[1:]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# "End Conversation" button is now handled in the main layout

# Initialize the conversation history if it doesn't exist
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

# Check if the conversation history is not empty before accessing the last item
if st.session_state.conversation_history:
    disabled = st.session_state.conversation_history[-1]["role"] == "user"
else:
    disabled = False

# Process user input
if st.session_state.interview_started and prompt:
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Add user message to conversation history
        st.session_state.conversation_history.append({"role": "user", "content": prompt})
        save_conversation([{"role": "user", "content": prompt}], st.session_state.conversation_id)

        # Generate assistant response
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
            response_text = response.content[0].text if isinstance(response.content, list) else response.content
        except Exception as e:
            if "invalid_api_key" in str(e).lower():
                st.error("Invalid API key. Please check your Anthropic API key in the Streamlit secrets.")
            else:
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
