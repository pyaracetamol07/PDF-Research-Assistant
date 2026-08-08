
print("vector_db.py imported")#

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import tempfile
import os

load_dotenv()

embeddings=GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)

def create_vector_db(uploaded_files):
    print("Entered create_vector_db")#
    

    print("========== DEBUG ==========")
    print("Entered create_vector_db")
    print("===========================")

    all_documents = []
    all_documents=[]
    for pdf in uploaded_files:

        print("File Name:", pdf.name)#
        print("File Size:", pdf.size)#

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as temp_file:
            temp_file.write(pdf.getvalue())
            temp_path= temp_file.name

        print("Temp Path:", temp_path) #
        print("Temp File Size:", os.path.getsize(temp_path))#
        print("Temp file size:", os.path.getsize(temp_path))#

        loader=PyPDFLoader(temp_path)
        documents=loader.load()
        for document in documents:
            document.metadata["source"]= pdf.name
        all_documents.extend(documents)
        os.remove(temp_path)
    text_splitter=RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks=text_splitter.split_documents(all_documents)

    vector_store=Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="chroma_db"
    )

    return vector_store



