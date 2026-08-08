import os
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

embeddings=GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)

db= Chroma(
    persist_directory="chroma_db",
    embedding_function= embeddings
)
retriever= db.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"k":3, "score_threshold":0.4}
)
llm= ChatGoogleGenerativeAI(
    model="models/gemini-3.5-flash-lite"
)
tavily= TavilyClient(
    api_key= os.getenv("TAVILY_API_KEY")
)

prompt= ChatPromptTemplate.from_template("""
You are a helpful AI assistant.

Answer the question ONLY using the provided context.
If the context comes from uploaded documents, answer from those documents.
If the context comes from a web search, answer only from the web context.
Do not use your own knowledge.
If the answer is not present in the context, reply:
"I don't know based on the provided context."

Context:
{context}

Question:
{question}

""")

verification_prompt= ChatPromptTemplate.from_template("""
        You are an AI verifier.
        
        Question:
        {query}
        
        Context:
        {context}

        Answer:
        {answer}

        Check whether the answer is fully supported by the context.
        If the answer contains information that is not supported by the context, remove or correct that information.
        Do not add information from your own knowledge
        If the contextdoes not contain enough information to answer to the question, return exactly:
        I don't know based on the provided context.
        Otherwise return only the corrected final answer.
        """
    )

def response_to_text(response):
    content=response.content
    if isinstance(content,str):
        return content.strip()
    if isinstance(content,list):
        text_parts=[]
        for item in content:
            if isinstance(item,str):
                text_parts.append(item)
            elif isinstance(item,dict):
                if "text" in item:
                    text_parts.append(str(item["text"]))
                else:
                    text_parts.append(str(item))
            else:
                text_parts.append(str(item))

        return "\n".join(text_parts).strip()
    
    return str(content).strip()
    
def ask_ques(query, web_search=False):
    print("=" * 60) 
    print("ask_ques() called") 
    print("Query:", query) 
    print("Web search:", web_search) 
    print("=" * 60)

    if web_search:
        print(">>>WEB SERACH MODE")
        print(">>>Calling Tavily.....")

        web_results=tavily.search(
            query=query, max_results=3
        )
        web_context= ""
        web_sources=[]

        for result in web_results.get("results",[]):
            content=result.get("content","")
        
            if content:
                web_context+=(content+"\n\n")
            title=result.get("title", "Untitled source")
            url= result.get("url","")
            web_sources.append(f"{title} --- {url}")

        if not web_context.strip():
            print("Tavily returned no useful content")
            return("I couldn't find relevant information on the web")
                    
        print("WEB RESUKTS FOUND:",
              len(web_results.get("results",[])))
              
        web_prompt=prompt.invoke({"context": web_context, "question": query})
            
        response = llm.invoke(web_prompt)
        init_ans= response_to_text(response)
        print("INITIAL WEB ANSWER")
        print(init_ans)
        verification_input= verification_prompt.invoke({
                    "query":query,
                    "context":web_context,
                    "answer":init_ans
                })
        verified_response=llm.invoke(verification_input)

        final_answer=response_to_text(verified_response)
            
        final_answer+=("\n\nSources:\n")
        for source in web_sources:
                final_answer+=(
                    "-"+source+"\n"
                )
        return final_answer
    print("PDF SEARCH MODE")
    results= retriever.invoke(query)

    print("Retrieved Chunks:", len(results))

    if len(results)==0:
        print("No relevant PDFs found.")
        return "WEB SEARCH REQUIRED"
    
    sources= set()
    for doc in results:
        source=os.path.basename(doc.metadata.get("source","Unknown Source"))
        page= (doc.metadata.get("page",0)+1)
        sources.add(f"{source} (Page {page})")

    print("=" * 50)
    for i,doc in enumerate(results):
        print(f"\nChunk{i+1}")
        print(doc.metadata)
    print("="*60)

    context="\n\n\n".join([doc.page_content for doc in results])

   
    pdf_prompt = prompt.invoke(
            {
                "context": context,
                "question": query
            }
        )

    response = llm.invoke(pdf_prompt)

    initial_answer = response_to_text(response)


    print(">>> INITIAL PDF ANSWER:")
    print(initial_answer)


    if "i don't know" in initial_answer.lower():

            print("PDF COULD NOT ANSWER")

            return "WEB SEARCH REQUIRED"


    verification_input = verification_prompt.invoke(
            {
                "query": query,
                "context": context,
                "answer": initial_answer
            }
        )

    verified_response = llm.invoke(
            verification_input
        )

    final_answer = response_to_text(verified_response)


    if "i don't know" in final_answer.lower():

            print(
                "VERIFIER SAYS PDF COULD NOT ANSWER"
            )

            return "WEB SEARCH REQUIRED"

    final_answer += ("\n\nSources:\n")

    for source in sorted(sources):

            final_answer += (
                "- "
                + source
                + "\n"
            )


    return final_answer
        


