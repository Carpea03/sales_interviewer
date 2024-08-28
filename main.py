import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from anthropic import Anthropic
import os
from datetime import datetime
import uuid
import logging
import re
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import pymongo

# Set up logging
logging.basicConfig(filename='chatbot.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Load secrets
try:
    ANTHROPIC_API_KEY = st.secrets["ANTHROPIC_API_KEY"]
    email_user = st.secrets["EMAIL_USER"]
    email_password = st.secrets["EMAIL_PASSWORD"]
    email_server = st.secrets["EMAIL_SERVER"]
    email_port = st.secrets["EMAIL_PORT"]
    mongo_uri = st.secrets["mongo"]["uri"]
except KeyError as e:
    st.error(f"Missing required secret: {e}")
    logging.error(f"Missing required secret: {e}")
    st.stop()
except Exception as e:
    st.error(f"An error occurred while accessing secrets: {e}")
    logging.error(f"Error accessing secrets: {e}", exc_info=True)
    st.stop()

# Initialize Anthropic client
client = Anthropic(api_key=ANTHROPIC_API_KEY)

# Connect to MongoDB
try:
    mongo_client = MongoClient(mongo_uri)
    db = mongo_client.sales_interviewer
    conversations = db.conversations
    mongo_client.admin.command('ping')
    logging.info("Successfully connected to MongoDB Atlas")
except pymongo.errors.ConnectionFailure as e:
    st.error(f"Failed to connect to MongoDB Atlas: {e}")
    logging.error(f"Failed to connect to MongoDB Atlas: {e}", exc_info=True)
    st.stop()
except Exception as e:
    st.error(f"An unexpected error occurred: {e}")
    logging.error(f"An unexpected error occurred: {e}", exc_info=True)
    st.stop()

def strip_xml_tags(text):
    if isinstance(text, list):
        text = ' '.join(text)
    text = re.sub(r'</?response>', '', text)
    text = re.sub(r'</?insights_summary>', '', text)
    return text.strip()

def send_email(transcript, recipient):
    sender = email_user
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
            server.login(sender, email_password)
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"An error occurred while sending the email: {str(e)}")
        return False

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
    transcript = "\n".join([f"{message['role']}: {message['content']}" for message in st.session_state.conversation_history])
    email_receiver = "alexcarpenter2000@gmail.com , palacios.david88@gmail.com"

    try:
        if send_email(transcript, email_receiver):
            st.success('Thank you for the conversation. Have a great day!')
            logging.info(f"Conversation ended and email sent for conversation ID: {st.session_state.conversation_id}")
            st.session_state.conversation_history = []
            st.session_state.conversation_id = str(uuid.uuid4())
            st.session_state.interview_started = False
    except Exception as e:
        error_msg = f"An error occurred while ending the conversation: {str(e)}"
        logging.error(error_msg)
        st.error(error_msg)

# Set up the main layout
st.set_page_config(
    page_title="Sales Interviewer Chatbot",
    page_icon="💬",
    layout="wide",
)

# Sidebar
with st.sidebar:
    st.title("Sales Interviewer Chatbot")
    st.write("Welcome to the Sales Interviewer Chatbot. This AI-powered tool will conduct an interview to gather insights about your sales experiences.")

# Main content area
if 'interview_started' not in st.session_state:
    st.session_state.interview_started = False

if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

if 'conversation_id' not in st.session_state:
    st.session_state.conversation_id = str(uuid.uuid4())

if not st.session_state.interview_started:
    st.header("Ready to start your sales interview?")
    if st.button("Start Interview", use_container_width=True):
        st.session_state.interview_started = True
        st.session_state.conversation_history = [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello! It's great to meet you. I'm an AI assistant here to conduct an interview about your experiences as a sales professional. I'm looking forward to learning from you and gathering insights that could be helpful for other salespeople. To start off, could you tell me a bit about the organization or organizations you currently sell for?"}
        ]
        st.rerun()
else:
    # Chat interface
    for message in st.session_state.conversation_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # User input
    if prompt := st.chat_input("Your response:"):
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)

        # Add user message to conversation history
        st.session_state.conversation_history.append({"role": "user", "content": prompt})
        save_conversation([{"role": "user", "content": prompt}], st.session_state.conversation_id)

        # Generate assistant response
        with st.spinner("Thinking..."):
            try:
                response = client.messages.create(
                    model="claude-3-5-sonnet-20240620",
                    max_tokens=4096,
                    temperature=1,
                    system="""
                    You are an AI assistant tasked with conducting an interview with a sales professional to extract useful and actionable insights for other salespeople. Your goal is to engage in a natural conversation while gathering specific information about their experiences and practices.

                    Follow these guidelines when conducting the interview:

                    1. Start with introductory questions to build rapport and gather basic information.
                    2. Gradually transition to more in-depth questions about their selling experiences.
                    3. Be sure to ask about their interest in a platform that provides reviews on the companies they sell to.
                    4. Maintain a conversational tone throughout the interview.
                    5. Listen actively and ask relevant follow-up questions.
                    6. Probe deeper on interesting or unique sales approaches or experiences.
                    7. Mentally note key insights, strategies, or advice that could be valuable for other sales professionals.
                    8. After gathering sufficient information, summarize the key insights and actionable advice extracted from the interview.

                    Remember to maintain a friendly and professional tone throughout the interview, and adapt your questions based on the flow of the conversation and the information provided by the interviewee.
                    """,
                    messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.conversation_history],
                )
                response_text = response.content
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.stop()

        # Strip XML tags and display assistant response
        cleaned_response = strip_xml_tags(response_text)
        with st.chat_message("assistant"):
            st.write(cleaned_response)

        # Add assistant response to conversation history
        st.session_state.conversation_history.append({"role": "assistant", "content": cleaned_response})
        save_conversation([{"role": "assistant", "content": cleaned_response}], st.session_state.conversation_id)

    # End conversation button
    if st.button("End Conversation"):
        end_conversation()
        st.rerun()