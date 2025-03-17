import os
import logging
import chromadb
from chromadb.config import Settings
import coloredlogs
from uuid import uuid4
from flask import Flask
from flask import request
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_unstructured import UnstructuredLoader


# ------------------------------ Console information ------------------------------
logger = logging.getLogger(__file__)
coloredlogs.install(
    fmt='%(asctime)s, [%(filename)s]: %(levelname)s %(message)s')

# -------------------------------- Flask instance ---------------------------------
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# ------------------------------------ Routes -------------------------------------

@app.route("/embedding", methods=['GET'])
async def sync_SFTP_files():

    # Response body construction
    respDict = dict()

    logger.info("Starting Embedder...")

    # ------------------------------- Parameters -------------------------------
    # Extract request parameters
    url = request.args.get('url')
    if url is None:
        return {"message": "Param [url] must be provided"}, 400

    openai_api_key = request.headers.get('Openaiapikey')
    if openai_api_key is None:
        return {"message": "Header [openai_api_key] must be provided"}, 400
    os.environ["OPENAI_API_KEY"] = openai_api_key
    # ------------------------------- Load files -------------------------------
    loader = UnstructuredLoader(web_url=url)

    docs = []
    async for doc in loader.alazy_load():
        doc.id = doc.metadata.get('element_id')
        for key in doc.metadata.keys():
            doc.metadata[key] = str(doc.metadata[key])
        docs.append(doc)
    
    
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    client = chromadb.HttpClient(host='chroma', port=8000, settings=Settings(allow_reset=True, anonymized_telemetry=False))
    print(client)
    vector_store = Chroma(
        collection_name="web_data",
        embedding_function=embeddings,
        client=client
    )
        
    uuids = [str(uuid4()) for _ in range(len(docs))]
    vector_store.add_documents(documents=docs, ids=uuids)
    
    # Status Ok
    return {}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
