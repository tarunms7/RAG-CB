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
    
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    for link in soup.find_all('a'):
        href = link.get('href')
        if href and '/support/' in href:
            urls.append(href if href.startswith('http') else f"https://www.angelone.in{href}")
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
    """Heavy initial setup: load docs, split, embed, and persist."""
    global vectorstore
    persist_directory = "/tmp/chroma_db"
    os.makedirs(persist_directory, exist_ok=True)

    documents = []
    documents.extend(scrape_angel_one_support())

    pdf_dir = "pdfs"
    if os.path.exists(pdf_dir):
        pdf_files = [os.path.join(pdf_dir, f) for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
        documents.extend(load_pdf_documents(pdf_files))

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(documents)

    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=OpenAIEmbeddings(),
        persist_directory=persist_directory
    )
    return vectorstore


def get_vectorstore():
    """Lazy loader: only initialize once on first use."""
    global vectorstore
    if vectorstore is None:
        vectorstore = initialize_rag()
    return vectorstore


def create_conversation_chain():
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer"
    )
    vs = get_vectorstore()
    return ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(temperature=0),
        retriever=vs.as_retriever(),
        memory=memory,
        return_source_documents=False
    )


def respond(message, chat_history):
    """Handle the chat response"""
    try:
        conversation_chain = create_conversation_chain()
        result = conversation_chain.invoke({"question": message})
        chat_history.append({"role": "user", "content": message})
        chat_history.append({"role": "assistant", "content": result["answer"]})
        return "", chat_history
    except Exception as e:
        error_message = f"Sorry, I ran into a problem: {str(e)}"
        chat_history.append({"role": "user", "content": message})
        chat_history.append({"role": "assistant", "content": error_message})
        return "", chat_history


def create_interface():
    """Create the Gradio interface"""
    with gr.Blocks(title="Angel One Support Chatbot") as demo:
        gr.Markdown("# Angel One Support Chatbot")
        chatbot = gr.Chatbot(height=600, type="messages")
        with gr.Row():
            msg = gr.Textbox(
                placeholder="Ask a question about Angel One support...",
                show_label=False,
                container=False
            )
            submit = gr.Button("Send")

        submit.click(
            respond,
            inputs=[msg, chatbot],
            outputs=[msg, chatbot]
        )
        msg.submit(
            respond,
            inputs=[msg, chatbot],
            outputs=[msg, chatbot]
        )
    return demo


if __name__ == "__main__":
    demo = create_interface()
    demo.launch(server_name="0.0.0.0", server_port=7860)
