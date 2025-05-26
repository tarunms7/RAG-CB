import streamlit as st
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

# Keep track of our chat state
if "conversation" not in st.session_state:
    st.session_state.conversation = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "input_key" not in st.session_state:
    st.session_state.input_key = 0

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
    # Where we'll store our vector database
    persist_directory = "chroma_db"
    if not os.path.exists(persist_directory):
        os.makedirs(persist_directory)
    
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
    
    # Set up our conversation memory
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer"
    )
    
    # Create our main conversation chain
    conversation = ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(temperature=0),
        retriever=vectorstore.as_retriever(),
        memory=memory,
        return_source_documents=False  # We don't need to show sources to the user
    )
    
    return conversation

def display_message(role, message):
    """Make our chat messages look nice with different styles for user and bot"""
    if role == "You":
        st.markdown(f"""
        <div style='display: flex; justify-content: flex-end; margin: 10px 0;'>
            <div style='background-color: #007AFF; color: white; padding: 10px 15px; border-radius: 15px; max-width: 70%;'>
                {message}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style='display: flex; justify-content: flex-start; margin: 10px 0;'>
            <div style='background-color: #E9ECEF; color: black; padding: 10px 15px; border-radius: 15px; max-width: 70%;'>
                {message}
            </div>
        </div>
        """, unsafe_allow_html=True)

def main():
    st.title("Angel One Support Chatbot")
    
    # Set up our chatbot if it's not already running
    if st.session_state.conversation is None:
        with st.spinner("Getting everything ready..."):
            try:
                st.session_state.conversation = initialize_rag()
            except Exception as e:
                st.error(f"Oops! Something went wrong: {str(e)}")
                st.stop()
    
    # Create our chat display area
    chat_container = st.container()
    
    # Create our input area at the bottom
    input_container = st.container()
    
    # Show all our previous messages
    with chat_container:
        for role, message in st.session_state.chat_history:
            display_message(role, message)
    
    # Add some breathing room between chat and input
    st.markdown("<br>" * 2, unsafe_allow_html=True)
    
    # Set up our input area with a text box and send button
    with input_container:
        col1, col2 = st.columns([6, 1])
        with col1:
            user_question = st.text_input(
                "Ask a question about Angel One support:",
                key=f"user_input_{st.session_state.input_key}",
                label_visibility="collapsed"
            )
        with col2:
            send_button = st.button("Send", use_container_width=True)
    
    # Handle when the user asks a question
    if user_question and (send_button or user_question):
        with st.spinner("Thinking..."):
            try:
                # Get the bot's response
                response = st.session_state.conversation.invoke({"question": user_question})
                
                # Add the conversation to our history
                st.session_state.chat_history.append(("You", user_question))
                st.session_state.chat_history.append(("Bot", response["answer"]))
                
                # Clear the input box for the next question
                st.session_state.input_key += 1
                
                # Refresh the display
                st.rerun()
                
            except Exception as e:
                st.error(f"Something went wrong: {str(e)}")
                st.session_state.chat_history.append(("Bot", "Sorry, I ran into a problem. Could you try asking that again?"))

if __name__ == "__main__":
    main() 