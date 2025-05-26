# Angel One Support Chatbot

A Retrieval-Augmented Generation (RAG) chatbot trained on Angel One support documentation to assist users with their queries.

## Features

- Answers questions based on Angel One support documentation
- Responds with "I don't know" for questions outside the knowledge base
- User-friendly web interface
- Support for both web content and PDF documents
- Persistent chat history
- Modern, responsive UI

## Live Demo

[Add your deployed application URL here]

## Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Git

## Local Setup

1. Clone this repository:

```bash
git clone <repository-url>
cd RAG
```

2. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install the required packages:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root and add your OpenAI API key:

```bash
cp .env.example .env
# Edit .env with your OpenAI API key
```

5. Create a `pdfs` directory and add any PDF documents you want to include in the knowledge base:

```bash
mkdir pdfs
# Add your PDF files to the pdfs directory
```

## Running the Application Locally

1. Start the Streamlit application:

```bash
streamlit run app.py
```

2. Open your web browser and navigate to the URL shown in the terminal (typically http://localhost:8501)

## Deployment Options

### 1. Deploy on Streamlit Cloud (Recommended)

1. Push your code to a GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with your GitHub account
4. Click "New app"
5. Select your repository, branch, and main file (app.py)
6. Add your environment variables (OPENAI_API_KEY)
7. Click "Deploy"

### 2. Deploy on Heroku

1. Create a `Procfile`:

```
web: streamlit run app.py
```

2. Create a `runtime.txt`:

```
python-3.9.16
```

3. Install the Heroku CLI and deploy:

```bash
heroku create your-app-name
git push heroku main
heroku config:set OPENAI_API_KEY=your-api-key
```

### 3. Deploy on AWS

1. Create an EC2 instance
2. Install required packages
3. Set up environment variables
4. Use screen or systemd to run the application
5. Configure security groups for port 8501

## Project Structure

- `app.py`: Main application file containing the Streamlit interface and RAG implementation
- `requirements.txt`: List of Python dependencies
- `pdfs/`: Directory containing PDF documents for the knowledge base
- `.env`: Environment variables file (create this file with your OpenAI API key)
- `chroma_db/`: Directory for the vector database (created automatically)

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

[Add your chosen license here]

## Acknowledgments

- Angel One for their support documentation
- OpenAI for their language models
- Streamlit for the web framework
- LangChain for the RAG implementation
