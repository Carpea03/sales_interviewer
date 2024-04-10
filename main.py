import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import anthropic

# Streamlit app title and description
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
client = anthropic.Anthropic(api_key=anthropic_api_key)

# Initialize session state with an initial message
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm here to interview you. Let's start!"}
    ]

# Function to generate chatbot response using Anthropic API
def generate_response(prompt):
    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=4000,
        temperature=1,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    return response.completion.strip()

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response_text = generate_response(prompt)
            st.write(response_text)
            message = {"role": "assistant", "content": response_text}
            st.session_state.messages.append(message)

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

# Chatbot interview loop
def interview():
    st.write("Chatbot: Hello! I'm here to interview you. Let's start!")
    transcript = ""
    message_count = 0
    while True:
        user_input = st.text_input("You: ", key=f"user_input_{message_count}")
        message_count += 1
        if user_input.lower() in ["quit", "exit", "done"]:
            break
        transcript += f"You: {user_input}\n"
        prompt = f"{transcript}\nChatbot:"
        response_content = generate_response(prompt)
        response = response_content[0].text.strip()
        transcript += f"Chatbot: {response}\n"
        st.write(f"Chatbot: {response}")

    story_prompt = f"Based on the following interview transcript, write a compelling story about the interviewee:\n\n{transcript}"
    story_text = generate_response(story_prompt)
    st.write(f"\nGenerated Story:\n{story_text}")

    recipient_email = st.text_input("Enter your email address to receive the transcript and story:")
    if st.button("Send Email"):
        send_email(transcript, story_text, recipient_email)
        st.write("Email sent successfully!")

# Run the chatbot interview
if __name__ == "__main__":
    interview()