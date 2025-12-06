from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from typing import List, Optional
from dataclasses import dataclass

# BGE embeddings - state-of-the-art for retrieval
EMBEDDING_MODEL = "BAAI/bge-large-en-v1.5"
EMBEDDING_DIMENSION = 1024  # For Pinecone index config

@dataclass
class Source:
    text: str
    citation: str
    date: str
    author: Optional[str] = None

class RAGSystem:
    def __init__(self, index_name: str = "farrand-sources"):
        # Initialize BGE embeddings (top-tier retrieval quality)
        self.embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}  # BGE recommends normalization
        )

        # Initialize Pinecone
        # Note: This assumes PINECONE_API_KEY is set in environment variables
        try:
            pc = Pinecone()
            self.vectorstore = PineconeVectorStore(
                index=pc.Index(index_name),
                embedding=self.embeddings
            )
            self.retriever = self.vectorstore.as_retriever(
                search_kwargs={
                    "k": 5,
                    "filter": {"date_max": {"$lte": "1787-09-17"}}
                }
            )
        except Exception as e:
            print(f"Warning: Pinecone initialization failed: {e}. RAG system will not function correctly without valid credentials.")
            self.vectorstore = None
            self.retriever = None

    async def retrieve(self, query: str, delegate_name: str = None) -> List[Source]:
        """Retrieve relevant historical sources for a query."""
        if not self.retriever:
            return []
            
        # BGE recommends prefixing queries for better retrieval
        prefix = "Represent this sentence for searching relevant passages: "
        enhanced_query = f"{prefix}{delegate_name}: {query}" if delegate_name else f"{prefix}{query}"

        docs = await self.retriever.ainvoke(enhanced_query)
        return [self._doc_to_source(doc) for doc in docs]

    def _doc_to_source(self, doc) -> Source:
        return Source(
            text=doc.page_content,
            citation=f"【{doc.metadata.get('collection', 'unknown')}, {doc.metadata.get('doc_id', 'unknown')}】",
            date=doc.metadata.get('date', 'unknown'),
            author=doc.metadata.get('author')
        )

    @classmethod
    def ingest_documents(cls, documents: List[dict], index_name: str = "farrand-sources"):
        """Ingest documents into Pinecone."""
        embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )

        texts = [doc["content"] for doc in documents]
        metadatas = [
            {
                "collection": doc["collection"],
                "doc_id": doc["id"],
                "date": doc["date"],
                "author": doc.get("author", "unknown")
            }
            for doc in documents
        ]

        PineconeVectorStore.from_texts(
            texts=texts,
            embedding=embeddings,
            metadatas=metadatas,
            index_name=index_name
        )
