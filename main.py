import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from anthropic import Anthropic
import tornado.websocket
import os
from datetime import datetime

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

# Function to append new messages to the conversation log file
def save_conversation(new_messages):
    try:
        with open("conversation_log.txt", "a") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"\n--- New messages at {timestamp} ---\n")
            for message in new_messages:
                f.write(f"{message['role']}: {message['content']}\n")
            f.write("\n")
    except Exception as e:
        st.error(f"An error occurred while saving the conversation: {str(e)}")

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
# Assertions for email_password, email_server, and email_port could be added here as needed

# Initialize Anthropic client
client = Anthropic(api_key=ANTHROPIC_API_KEY)

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
    save_conversation([{"role": "user", "content": prompt}])

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

If you have gathered enough information to summarize insights, include a summary at the end of your response:

<insights_summary>
[List of key insights and actionable advice for other sales professionals]
</insights_summary>

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
    save_conversation([{"role": "assistant", "content": response_text}])

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
