# PDF Research Assistant

PDF Research Assistant is an AI-powered document research tool that lets users upload PDFs, ask questions about their contents, and receive answers grounded in the uploaded documents with relevant sources. If the information is not available in the uploaded documents, the user can explicitly choose to search the web for additional information.

## Features

* Upload up to 5 PDF files
* Ask questions about uploaded documents
* AI-generated answers based on the uploaded documents
* PDF name and page number shown as sources
* Chat history for previous questions and answers
* Optional web search when information is not found in the uploaded PDFs
* Web sources shown for web-based answers
* Answer verification to improve reliability


## Tech Stack

Python · Streamlit · LangChain · Google Gemini · ChromaDB · PyPDF · Tavily

## Project Structure

app.py             → Streamlit application

rag.py             → Retrieval, answer generation, verification and web search

vector_db.py       → PDF processing and vector database creation

requirements.txt  → Project dependencies

## Run Locally

1. Install the dependencies:

    pip install -r requirements.txt


2. Create a .env file with your API keys:

    GOOGLE_API_KEY=your_google_api_key

    TAVILY_API_KEY=your_tavily_api_key


3. Run the application:

    streamlit run app.py


## GitHub Repository

To view the entire repository: https://github.com/pyaracetamol07/PDF-Research-Assistant.git

## Live Application

Open the application: https://pdf-research-assistant-3boswrfzuxuwxs9gc3gcxj.streamlit.app/

## Demo Video

Coming soon.

## Improvement Write-up

The current version focuses on building a working PDF-first research assistant with document retrieval, answer generation, verification and optional web search. One improvement I would like to make is a better and more interactive interface so that the application feels more like a proper research assistant rather than a basic question-answering page.

I would also like to turn the current interface into a proper conversational chatbot where users can have a continuous conversation about the information they uploaded. This would allow follow-up questions without treating every question as completely separate. The chatbot could maintain relevant conversation context while still grounding its answers in the uploaded documents.

Another improvement would be adding OCR support for scanned PDFs, since image-based documents may not provide usable text through normal PDF extraction. Retrieval could also be improved using hybrid search and reranking for questions where relevant information is spread across different parts of a document.

In the future, I would also like to improve the source display, add document previews, and make it easier for users to understand exactly which part of a document was used to generate an answer.
