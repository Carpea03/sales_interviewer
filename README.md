Sales Interviewer Chatbot
This project is a Streamlit-based application that utilizes Anthropic's Claude 3.5 model to create an interactive chatbot. The chatbot interviews sales professionals and generates content based on their responses. Additionally, the application can send an email with the interview transcript and generated story.

Features
Interactive chatbot for interviewing sales professionals
Content generation based on user responses
Email functionality to send the interview transcript and generated content
Requirements
Python 3.7 or higher
Streamlit
SMTP library for email functionality
Tornado for websocket support
Setup and Installation
Clone the repository:

bash
Copy code
git clone https://github.com/yourusername/sales-interviewer-chatbot.git
cd sales-interviewer-chatbot
Install the required packages:

bash
Copy code
pip install streamlit anthropic smtplib tornado yagmail
Set up Streamlit secrets:

Create a file named .streamlit/secrets.toml in the root directory of your project with the following content:

toml
Copy code
[secrets]
ANTHROPIC_API_KEY = "your_anthropic_api_key"
EMAIL_USER = "your_email@example.com"
EMAIL_PASSWORD = "your_email_password"
EMAIL_SERVER = "smtp.your_email_provider.com"
EMAIL_PORT = 587
Run the Streamlit app:

bash
Copy code
streamlit run app.py
Usage
Open the Streamlit app in your browser.
Interact with the chatbot by providing responses to its questions.
The chatbot will generate content based on your responses.
At the end of the interview, the app will send an email with the interview transcript and generated content to the specified recipient.
Code Overview
Email Sending Function: The send_email function is responsible for sending an email with the interview transcript and generated story.
Streamlit Interface: The Streamlit app initializes the OpenAI client, manages the conversation history, and handles user input.
Conversation Handling: The chatbot engages in a conversation with the user, and responses are generated using OpenAI's GPT-4o model.
Email Sending: After the interview, the app extracts the article from the generated response, compiles the transcript, and sends it via email.
Configuration
Ensure the following configurations are set correctly in the secrets.toml file:

ANTHROPIC_API_KEY: Your Anthropic API key.
EMAIL_USER: Your email address used for sending emails.
EMAIL_PASSWORD: Your email password or app-specific password.
EMAIL_SERVER: The SMTP server of your email provider.
EMAIL_PORT: The SMTP port of your email provider (commonly 587 for TLS).
Troubleshooting
Ensure all required packages are installed.
Verify the API key and email credentials are correctly set in the secrets.toml file.
Check your internet connection and make sure the OpenAI API and SMTP server are accessible.
If you encounter websocket connection issues, try refreshing the page or restarting the Streamlit app.
License
This project is licensed under the MIT License. See the LICENSE file for more details.

Acknowledgements
Streamlit for the interactive web app framework.
Tornado for websocket support.

## Project Conventions

This project follows these conventions:

1. **Programming Language**: Python
2. **Code Style**: PEP 8
3. **Version Control**: GitHub Flow
4. **Testing**: Unit Testing with pytest
5. **Documentation**: Inline comments and docstrings
6. **Dependency Management**: requirements.txt with pip

For detailed conventions, please refer to the full conventions document in the project repository.