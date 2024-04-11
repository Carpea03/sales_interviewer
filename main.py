import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import anthropic

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
            max_tokens=4000,
            temperature=1,
        )

        # Display the streamed response
        response = st.write_stream(stream)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

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