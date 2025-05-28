---
title: Angel One Support Chatbot
emoji: 🤖
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 4.19.2
app_file: app.py
pinned: false
python_version: "3.11.12"
---

# Angel One Support Chatbot

A RAG (Retrieval Augmented Generation) based chatbot that provides support information about Angel One's services. The chatbot uses LangChain, OpenAI, and Gradio to create an interactive interface for users to get answers about Angel One's support documentation.

## Features

- Web scraping of Angel One's support documentation
- PDF document processing
- Vector-based semantic search
- Interactive chat interface
- Memory-aware conversations
- Real-time responses

## Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Internet connection for web scraping

## Installation

1. Clone the repository:

```bash
git clone <your-repo-url>
cd <your-repo-name>
```

2. Create a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory and add your OpenAI API key:

```
OPENAI_API_KEY=your-api-key-here
```

## Usage

1. Run the application:

```bash
python app.py
```

2. Open your web browser and navigate to the URL shown in the terminal (usually http://127.0.0.1:7860)

3. Start chatting with the bot about Angel One's services

## Project Structure

```
.
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (not tracked in git)
├── chroma_db/         # Vector database storage
└── pdfs/             # Directory for PDF documents (optional)
```

## Deployment

The application can be deployed on various platforms:

1. **Hugging Face Spaces** (Recommended)

   - Free hosting
   - Easy deployment
   - Built-in support for Gradio

2. **PythonAnywhere**

   - Free tier available
   - Good for Python applications
   - Easy setup

3. **Render**
   - Free tier available
   - Good performance
   - Easy deployment

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- LangChain for the RAG framework
- OpenAI for the language model
- Gradio for the web interface
- Angel One for the support documentation
