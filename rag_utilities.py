from langchain_aws import BedrockEmbeddings
from chromadb import PersistentClient
from functools import lru_cache
import os
from dotenv import load_dotenv
from langchain_chroma import Chroma

load_dotenv()

CHROMA_DIR = "./chroma_data" 

#LRU cache for Global Embedding
@lru_cache()
def get_embeddings():
    return BedrockEmbeddings(
        model_id="amazon.titan-embed-text-v2:0",
        region_name=os.getenv("AWS_REGION", "us-east-2"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )
chroma_client = PersistentClient(path=CHROMA_DIR)

collection_cache = {}

db_cache = {}

def get_rag_collection(rag_id: str):
    if rag_id in collection_cache:
        return collection_cache[rag_id]
    
    collection = chroma_client.get_or_create_collection(
        name=rag_id,
        metadata={"hnsw:space": "cosine"},
    )

    collection_cache[rag_id] = collection
    return collection


# Cache DB wrapper instances
@lru_cache(maxsize=100)
def get_cached_db(collection_name: str):
    """Get or create a cached Chroma DB instance"""
    embeddings = get_embeddings()
    return Chroma(
        client=chroma_client,
        collection_name=collection_name,
        embedding_function=embeddings
    )
