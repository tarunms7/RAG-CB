import gradio as gr
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
import requests
from bs4 import BeautifulSoup
import tempfile

# Load our environment variables (API keys, etc.)
load_dotenv()

# Global vectorstore
vectorstore = None

def scrape_angel_one_support():
    """Grab all the support content from Angel One's website"""
    base_url = "https://www.angelone.in/support"
    urls = []
    
    # First, get the main support page
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all the support links on the page
    for link in soup.find_all('a'):
        href = link.get('href')
        if href and '/support/' in href:
            urls.append(href if href.startswith('http') else f"https://www.angelone.in{href}")
    
    # Load all the content from these pages
    loader = WebBaseLoader(urls)
    return loader.load()

def load_pdf_documents(pdf_files):
    """Read and extract text from PDF files"""
    documents = []
    for pdf_file in pdf_files:
        loader = PyPDFLoader(pdf_file)
        documents.extend(loader.load())
    return documents

def initialize_rag():
    """Set up our RAG system with all the necessary components"""
    global vectorstore
    
    # Where we'll store our vector database
    persist_directory = "/mnt/data/chroma_db"
    os.makedirs(persist_directory, exist_ok=True)
    
    # Start collecting all our documents
    documents = []
    
    # Get all the web content first
    web_docs = scrape_angel_one_support()
    documents.extend(web_docs)
    
    # Then add any PDFs we have
    pdf_dir = "pdfs"
    if os.path.exists(pdf_dir):
        pdf_files = [os.path.join(pdf_dir, f) for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
        pdf_docs = load_pdf_documents(pdf_files)
        documents.extend(pdf_docs)
    
    # Break down our documents into smaller chunks for better processing
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    splits = text_splitter.split_documents(documents)
    
    # Create our vector store to store and search through our documents
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=OpenAIEmbeddings(),
        persist_directory=persist_directory
    )
    
    return vectorstore

def create_conversation_chain():
    """Create a new conversation chain with the vectorstore"""
    global vectorstore
    
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer"
    )
    
    return ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(temperature=0),
        retriever=vectorstore.as_retriever(),
        memory=memory,
        return_source_documents=False
    )

def respond(message, chat_history):
    """Handle the chat response"""
    try:
        # Create a new conversation chain for each interaction
        conversation = create_conversation_chain()
        response = conversation.invoke({"question": message})
        
        # Convert messages to Gradio format
        chat_history.append({"role": "user", "content": message})
        chat_history.append({"role": "assistant", "content": response["answer"]})
        
        return "", chat_history
    except Exception as e:
        error_message = f"Sorry, I ran into a problem: {str(e)}"
        chat_history.append({"role": "user", "content": message})
        chat_history.append({"role": "assistant", "content": error_message})
        return "", chat_history

def create_interface():
    """Create the Gradio interface"""
    # Initialize RAG system
    initialize_rag()
    
    # Create the chat interface
    with gr.Blocks(title="Angel One Support Chatbot") as demo:
        gr.Markdown("# Angel One Support Chatbot")
        
        # Chat history
        chatbot = gr.Chatbot(height=600, type="messages")
        
        # Message input
        with gr.Row():
            msg = gr.Textbox(
                placeholder="Ask a question about Angel One support...",
                show_label=False,
                container=False
            )
            submit = gr.Button("Send")
        
        # Handle submit
        submit.click(
            respond,
            inputs=[msg, chatbot],
            outputs=[msg, chatbot]
        )
        
        # Handle enter key
        msg.submit(
            respond,
            inputs=[msg, chatbot],
            outputs=[msg, chatbot]
        )
    
    return demo

if __name__ == "__main__":
    demo = create_interface()
    demo.launch() 