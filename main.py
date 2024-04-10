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
    return response.messages[-1]["content"][0]["text"].strip()

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
    # Initialize the conversation history if not already done
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    
    st.title("Chatbot Interviewer")
    st.write("This chatbot will interview you and generate a compelling story based on your responses.")
    
    # Display previous conversation
    for role, message in st.session_state.conversation_history:
        if role == "user":
            st.chat_message(message, is_user=True)
        else:
            st.chat_message(message, is_user=False)
    
    # User input
    user_input = st.text_input("Your message:", key="user_input")
    
    if st.button("Send"):
        # Append user input to conversation history
        st.session_state.conversation_history.append(("user", user_input))
        
        # Generate response from the chatbot
        prompt = "\n".join([msg for _, msg in st.session_state.conversation_history]) + "\nChatbot:"
        chatbot_response = generate_response(prompt)  # Ensure generate_response is adjusted to use the Anthropic API
        
        # Append chatbot response to conversation history
        st.session_state.conversation_history.append(("chatbot", chatbot_response))
        
        # Clear the input box after sending
        st.session_state.user_input = ""
        
        # Display chatbot response
        st.chat_message(chatbot_response, is_user=False)

    # Optional: Code to handle story generation and email sending goes here

# Ensure this function is called to run the chatbot
if __name__ == "__main__":
    interview()