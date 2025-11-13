#
# EMBEDDING_INSTANCE = None
#
# def get_embedding():
#     global EMBEDDING_INSTANCE
#     if EMBEDDING_INSTANCE is None:
#         from langchain_huggingface import HuggingFaceEmbeddings
#         EMBEDDING_INSTANCE = HuggingFaceEmbeddings(
#             model_name="all-MiniLM-L6-v2",
#             model_kwargs={"device": "cpu"}
#         )
#     return EMBEDDING_INSTANCE