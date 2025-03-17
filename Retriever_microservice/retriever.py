import os
import logging
import chromadb
import coloredlogs
from flask import Flask
from flask import request
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.combine_documents import create_stuff_documents_chain


# ------------------------------ Console information ------------------------------
logger = logging.getLogger(__file__)
coloredlogs.install(
    fmt='%(asctime)s, [%(filename)s]: %(levelname)s %(message)s')

# -------------------------------- Flask instance ---------------------------------
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# ------------------------------------ Routes -------------------------------------

@app.route("/retriever", methods=['GET'])
async def sync_SFTP_files():

    # Response body construction
    respDict = dict()

    logger.info("Starting Retriever...")

    # ------------------------------- Parameters -------------------------------
    # Extract request parameters
    query = request.args.get('query')
    if query is None:
        return {"message": "Param [query] must be provided"}, 400

    openai_api_key = request.headers.get('Openaiapikey')
    if openai_api_key is None:
        return {"message": "Header [openai_api_key] must be provided"}, 400
    os.environ["OPENAI_API_KEY"] = openai_api_key
    # ------------------------------- Load files -------------------------------
    
    client = chromadb.HttpClient(host='localhost', port=8000)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vector_store = Chroma(
        collection_name="web_data",
        embedding_function=embeddings,
        client=client
    )
    retriever = vector_store.as_retriever()
    docs = retriever.invoke(query)
    
    chat = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    
    SYSTEM_TEMPLATE = """
    Answer the user's questions based on the below context. 
    If the context doesn't contain any relevant information to the question, don't make something up and just say "I don't know":

    <context>
    {context}
    </context>
    """

    question_answering_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                SYSTEM_TEMPLATE,
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )

    document_chain = create_stuff_documents_chain(chat, question_answering_prompt)
    
    result = document_chain.invoke(
        {
            "context": docs,
            "messages": [
                HumanMessage(content="O que é a Hotmart?")
            ],
        }
    )
    
    # Status Ok
    return result, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
