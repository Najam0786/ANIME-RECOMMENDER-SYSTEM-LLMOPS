import os
from pathlib import Path
from typing import List, Dict, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from utils.logger import get_logger
from utils.custom_exception import CustomException
from config.config import Config

logger = get_logger(__name__)

class VectorStoreBuilder:
    def __init__(
        self,
        csv_path: str,
        persist_dir: str = "chroma_db",
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        self.csv_path = csv_path
        self.persist_dir = persist_dir
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.embedding = self._initialize_embeddings(Config.EMBEDDING_MODEL)

    def _initialize_embeddings(self, model_name: str) -> HuggingFaceEmbeddings:
        """Initialize embedding model with proper configuration"""
        try:
            return HuggingFaceEmbeddings(
                model_name=model_name,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
        except Exception as e:
            raise CustomException("Failed to initialize embeddings", e)

    def build_and_save_vectorstore(self) -> None:
        """Build and persist vector store"""
        try:
            documents = self._load_documents()
            chunks = self._chunk_documents(documents)
            self._create_vector_store(chunks)
        except Exception as e:
            raise CustomException("Vector store creation failed", e)

    def _load_documents(self) -> List[Document]:
        """Load documents from CSV"""
        try:
            loader = CSVLoader(
                file_path=self.csv_path,
                encoding='utf-8',
                csv_args={'fieldnames': ['combined_info']}
            )
            documents = loader.load()
            if not documents:
                raise ValueError("No documents loaded from CSV")
            return documents
        except Exception as e:
            raise CustomException("Document loading failed", e)

    def _chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks"""
        try:
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap
            )
            return splitter.split_documents(documents)
        except Exception as e:
            raise CustomException("Document splitting failed", e)

    def _create_vector_store(self, chunks: List[Document]) -> None:
        """Create and persist Chroma vector store"""
        try:
            Chroma.from_documents(
                documents=chunks,
                embedding=self.embedding,
                persist_directory=self.persist_dir
            )
        except Exception as e:
            raise CustomException("Vector store creation failed", e)

    def load_vector_store(self):
        """Load existing vector store"""
        try:
            return Chroma(
                persist_directory=self.persist_dir,
                embedding_function=self.embedding
            )
        except Exception as e:
            raise CustomException("Failed to load vector store", e)