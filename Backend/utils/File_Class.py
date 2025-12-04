from dotenv import load_dotenv
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_chroma import Chroma

from utils.rag_utilities import get_embeddings, get_rag_collection, chroma_client, collection_cache

load_dotenv()

class PrepareFile:
    def __init__(self, file):
        self.data_path = file

    def load_documents(self):
        """Load documents from a PDF file."""
        document_loader = PyPDFLoader(self.data_path)
        return document_loader.load()

    def doc_splitter(self, documents: list[Document]):
        """Split documents into chunks."""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,
            chunk_overlap=30,
            length_function=len,
            is_separator_regex=False
        )
        return text_splitter.split_documents(documents)

    def id_chunks(self, chunks):
        """Assign unique IDs to chunks."""
        for i, chunk in enumerate(chunks):
            source = os.path.basename(chunk.metadata.get("source", "unknown"))
            page = chunk.metadata.get("page", 0)
            chunk_id = f"{source}_page{page}_chunk{i}"
            chunk.metadata["id"] = chunk_id
        return chunks

    # def save_to_chromadb(self, chunks, collection_name: str, persist_directory: str = "./chroma_data"):
    #     """
    #     Save chunks to ChromaDB using cached embeddings and cached collection.
        
    #     Args:
    #         chunks: List of Document chunks with IDs
    #         collection_name: Name of the collection
    #         persist_directory: Directory to persist ChromaDB data
    #     """

    #     # Get cached embedding function
    #     embedding_fn = get_embeddings()

    #     # Get cached collection object
    #     _ = get_rag_collection(collection_name)  # ensures collection exists in cache

    #     # Use Chroma wrapper to add documents with embeddings

    #     db = Chroma(
    #     #   client=get_rag_collection.collection_cache.get(collection_name) or get_rag_collection(collection_name),
    #         client=collection_cache.get(collection_name) or get_rag_collection(collection_name),
    #         collection_name=collection_name,
    #         embedding_function=embedding_fn,
    #     )

    #     db.add_documents(chunks)

    #     print(f"✓ Saved {len(chunks)} chunks to collection '{collection_name}'")
    def save_to_chromadb(self, chunks: list[Document], collection_name: str, persist_directory: str):
            """
            Saves a list of document chunks to a ChromaDB collection using the client.
            The Chroma.from_documents method correctly handles collection creation.
            """
            embeddings = get_embeddings()
            
            # Chroma.from_documents ensures the collection exists (or creates it) and adds the chunks.
            # It requires the raw chroma_client object, not a cached Collection object.
            try:
                db = Chroma.from_documents(
                    documents=chunks,
                    embedding=embeddings,
                    client=chroma_client,
                    collection_name=collection_name,
                    persist_directory=persist_directory # Note: persist_directory is often ignored when client is provided, but included for completeness.
                )
                print(f"Successfully saved {len(chunks)} chunks to Chroma collection: {collection_name}")
                return db
            except Exception as e:
                print(f"Error saving to ChromaDB for collection {collection_name}: {e}")
                raise