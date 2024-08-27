# Sales Interviewer Chatbot

This project is a Streamlit-based application that utilizes Anthropic's Claude 3.5 model to create an interactive chatbot for interviewing sales professionals. The chatbot conducts in-depth interviews, gathers insights, and stores conversation data for future analysis. It also includes functionality to send interview transcripts via email.

## Features

- Interactive chatbot for interviewing sales professionals
- Natural language processing using Anthropic's Claude 3.5 model
- Conversation history management using Streamlit session state
- Permanent storage of conversations using MongoDB Atlas
- Email functionality to send interview transcripts
- Logging for error tracking and debugging
## Requirements

- Python 3.7 or higher
- Streamlit
- Anthropic API client
- PyMongo (with srv extras for MongoDB Atlas support)
- SMTP library for email functionality
## Setup and Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/sales-interviewer-chatbot.git
   cd sales-interviewer-chatbot
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up Streamlit secrets:
   Create a file named `.streamlit/secrets.toml` in the root directory of your project with the following content:
   ```toml
   [secrets]
   ANTHROPIC_API_KEY = "your_anthropic_api_key"
   EMAIL_USER = "your_email@example.com"
   EMAIL_PASSWORD = "your_email_password"
   EMAIL_SERVER = "smtp.your_email_provider.com"
   EMAIL_PORT = 587

   [mongo]
   uri = "your_mongodb_atlas_connection_string"
   ```

4. Run the Streamlit app:
   ```bash
   streamlit run main.py
   ```
## Usage

1. Open the Streamlit app in your browser.
2. The chatbot will start the interview with introductory questions.
3. Respond to the chatbot's questions about your sales experiences.
4. The conversation will flow naturally, with the chatbot asking follow-up questions based on your responses.
5. At any point, you can click the "End Conversation" button to finish the interview.
6. The app will send an email with the interview transcript to the specified recipients.
7. Conversation data is stored in MongoDB Atlas for future analysis.
## Code Overview

- **Streamlit Interface**: The main.py file sets up the Streamlit app, manages the conversation flow, and handles user input.
- **Anthropic API Integration**: The app uses the Anthropic API client to generate responses using the Claude 3.5 model.
- **Conversation Management**: Conversation history is managed using Streamlit's session state and permanently stored in MongoDB Atlas.
- **Email Functionality**: The `send_email` function is responsible for sending the interview transcript via email.
- **Error Handling and Logging**: The app includes comprehensive error handling and logging for debugging and monitoring.
- **Data Processing**: Functions for cleaning and processing chatbot responses, including stripping XML tags.
## Configuration

Ensure the following configurations are set correctly in the `secrets.toml` file:

- `ANTHROPIC_API_KEY`: Your Anthropic API key
- `EMAIL_USER`: Your email address used for sending emails
- `EMAIL_PASSWORD`: Your email password or app-specific password
- `EMAIL_SERVER`: The SMTP server of your email provider
- `EMAIL_PORT`: The SMTP port of your email provider (commonly 587 for TLS)
- `mongo.uri`: Your MongoDB Atlas connection string
## Troubleshooting

- Ensure all required packages are installed using the `requirements.txt` file.
- Verify that the Anthropic API key, email credentials, and MongoDB URI are correctly set in the `secrets.toml` file.
- Check your internet connection and make sure the Anthropic API, SMTP server, and MongoDB Atlas are accessible.
- If you encounter any issues, check the `chatbot.log` file for error messages and debugging information.
- For persistent problems, try clearing your browser cache or restarting the Streamlit app.
## License

This project is licensed under the MIT License. See the LICENSE file for more details.

## Acknowledgements

- Streamlit for the interactive web app framework
- Anthropic for the Claude 3.5 language model
- MongoDB Atlas for cloud-based data storage

## Project Conventions

This project follows these conventions:

1. **Programming Language**: Python
2. **Code Style**: PEP 8
3. **Version Control**: GitHub Flow
4. **Testing**: Unit Testing with pytest
5. **Documentation**: Inline comments and docstrings
6. **Dependency Management**: requirements.txt with pip

For detailed conventions, please refer to the full conventions document in the project repository.