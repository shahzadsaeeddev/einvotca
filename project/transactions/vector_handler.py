# from langchain_community.vectorstores.qdrant import Qdrant
# from .embedding_manager import get_embedding
# embedding = get_embedding()
# class QdrantVectorHandler:
#     def __init__(
#         self,
#         host: str = "qdrant",
#         port: int = 6333,
#     ):
#         self.host = host  # ✅ fixed
#         self.port = port  # ✅ fixed
#
#     def create_vectors_data(self, doc: dict):
#         content = doc.get("content")
#         metadata = doc.get("metadata", {})
#         collection_name = doc.get("tenant_id")
#         doc_id = doc.get("id")
#
#         print("INVOICE CONTENT", content)
#
#         # 🛡 Validate & Convert content
#         if isinstance(content, str):
#             content = [content]
#         elif not isinstance(content, list):
#             raise ValueError("content must be a string or a list of strings")
#
#         # 🛡 Fix metadata to match content length
#         if isinstance(metadata, dict):
#             metadata = [metadata for _ in range(len(content))]
#         elif isinstance(metadata, list) and len(metadata) != len(content):
#             raise ValueError("metadata list length must match content length")
#
#         print("data ready for invoice creation",metadata)
#
#         # 🛡 Fix ids
#         ids = [doc_id for _ in range(len(content))]
#         print("IDS", ids)
#         # ✅ Call Qdrant.from_texts safely
#         # try:
#         qdrant = Qdrant.from_texts(
#             texts=content,
#             embedding=embedding,
#             metadatas=metadata,
#             ids=ids,
#             url=f"http://{self.host}:{self.port}",
#             collection_name=collection_name
#         )
#         print("QDRANT", qdrant)
#         print(f"✅ Stored {len(content)} documents in Qdrant collection '{collection_name}'")
#
#         # except Exception as e:
#         #     print(f"❌ Qdrant error: {e}")