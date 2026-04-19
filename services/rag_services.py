import os
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    CSVLoader,
    Docx2txtLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from config import GROQ_API_KEY

#Global initialization
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
#Global (in-memory store)
vector_store = None

def load_document(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
    elif ext == ".txt":
        loader = TextLoader(file_path)
    elif ext == ".csv":
        loader = CSVLoader(file_path)
    elif ext == ".docx":
        loader = Docx2txtLoader(file_path)
    else:
        raise ValueError("Unsupported file type")

    return loader.load()

def process_document(file_path):
    global vector_store

    #1. Load document
    documents = load_document(file_path)

    #2. Chunk
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )
    docs = splitter.split_documents(documents)
    
    # 3. Embeddings
    

    #4. Store in FAISS
    vector_store = FAISS.from_documents(docs, embeddings)

    return "Document processed successfully"


def ask_question(question):
    global vector_store

    if vector_store is None:
        return "No documents uploaded yet."

    #5. Retrieve
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    relevant_docs = retriever.invoke(question)

    context = "\n".join([doc.page_content for doc in relevant_docs])

    #6 LLM
    llm = ChatGroq(model_name="llama-3.1-8b-instant", groq_api_key=GROQ_API_KEY)

    #prompt
    prompt = f"""Use the following context to answer the question.
    
    Context:
    {context}
    
    Question: {question}
    """ 

    response = llm.invoke(prompt)

    return response.content