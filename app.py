import streamlit as st
import rag
from rag import ask_ques 
from vector_db import create_vector_db
import vector_db

print ("RAG FILE:", rag.__file__)
print ("ASK_QUES::", rag.ask_ques)
print(vector_db.__file__)

st.title(" PDF Research Assistant ")

uploaded_files= st.file_uploader(
    "Uploaded PDFs",
    type="pdf",
    accept_multiple_files=True
)

if uploaded_files:
    st.write("Uploaded Files:")
    for pdf in uploaded_files:
        st.write("*", pdf.name)

if uploaded_files and len(uploaded_files)>5:
    st.error("maximum 5 PDFs allowed :(( ")
    st.stop()


if "messages" not in st.session_state:
    st.session_state.messages=[]

if "database_ready" not in st.session_state:
    st.session_state.database_ready=False

process_button_clicked=st.button("Process Documents")

if process_button_clicked:

    with st.spinner("Processing the uploaded files...."):
        if not uploaded_files:
            st.warning("Kindly upload the files :)")
        else:
            try:
                create_vector_db(uploaded_files)
                st.session_state.database_ready =True
                st.success("Documents processed successfully!! XD")
            except Exception as e:
                st.error(f"Processing failed: {e}")


query= st.text_input("Ask your question: ")
ask_button_clicked= st.button("Ask")

if st.session_state.database_ready:
    if ask_button_clicked:

        if not query.strip():
            st.warning("Kindly enter a question !")
    
        else:
            st.session_state.messages.append(
                {
                    "role":"user",
                    "content": query
                }
            )
            answer=None

            try:
                with st.spinner("Thinking....."):
                    answer= ask_ques(query)

                    if (answer == "WEB SEARCH REQUIRED"):
                        st.session_state.web_search_query=query
                        st.warning("Answer not found in the uploaded PDFs.")
                    else:    
                        st.session_state.messages.append(
                            {
                                "role": "assistant",
                                "content":answer
                            }
                        )
            except Exception as e:
                st.error(f"Something went wrong: {e}")
            st.write(answer)

    if "web_search_query" in st.session_state:
        
        web_search_button_clicked=st.button("Search the web?? :O")
        if web_search_button_clicked:
            with st.spinner("Searching the web..."):
                try:
                    answer= ask_ques(st.session_state.web_search_query, web_search= True)
                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": answer
                        }
                    )
                    st.write(answer)
                    del st.session_state.web_search_query
                except Exception as e:
                    st.error(f"Web search failed : {e}")

if not st.session_state.database_ready: 
    st.info( "Kindly process the documents first :)" )




for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
    





