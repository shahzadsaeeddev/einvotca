import time

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores.qdrant import Qdrant
import uuid


def make_uuid(text):
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, text))


QDRANT_HOST = "localhost"
QDRANT_HTTP_PORT = 6333
QDRANT_COLLECTION_NAME = "invoice_collection"


def store_doc_in_qdrant(doc):
    try:
        content = doc["content"]
        metadata = doc.get("metadata", {})

        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        time.sleep(5)
        Qdrant.from_texts(texts=[content], embedding=embeddings, metadatas=[metadata], ids=[doc['id']],
                          url=f"http://{QDRANT_HOST}:{QDRANT_HTTP_PORT}", collection_name=doc['id'], )
        time.sleep(3)
        return True
    except Exception as e:
        print("Qdrant error:", e)
        return False

