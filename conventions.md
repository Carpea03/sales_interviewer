# Project Conventions

This document outlines the conventions used in the Sales Interviewer Chatbot project.

## Programming Language
- Python 3.7 or higher

## Code Style
- Follow PEP 8 guidelines for Python code style
- Use 4 spaces for indentation
- Maximum line length of 100 characters

## Version Control
- Use Git for version control
- Follow the GitHub Flow branching strategy
- Write clear, concise commit messages

## AI Model
- Use Anthropic's Claude 3.5 model for natural language processing
- Keep the model version up to date (currently using 'claude-3-opus-20240229')

## API Usage
- Use the Anthropic Python client library for API calls
- Store API keys securely in Streamlit secrets

## Testing
- Write unit tests using pytest
- Aim for high test coverage, especially for critical functions

## Documentation
- Use inline comments for complex code sections
- Write clear docstrings for functions and classes
- Keep the README.md file up to date with project information and setup instructions

## Dependency Management
- Use requirements.txt for managing Python dependencies
- Keep dependencies up to date, but be cautious of breaking changes

## Error Handling
- Use try-except blocks for error-prone operations
- Provide clear error messages to users

## Security
- Never commit sensitive information (like API keys) to the repository
- Use environment variables or secure secret management for sensitive data

## Code Reviews
- Conduct code reviews for all pull requests
- Ensure code adheres to these conventions before merging

## Conversation Logging
- Save all conversations between the chatbot and users
- Use a structured format (e.g., JSON) for storing conversation data
- Include timestamps, user inputs, and chatbot responses in the logs
- Store conversation logs in a dedicated directory within the project

These conventions are subject to change as the project evolves. Always refer to the latest version of this document in the repository.