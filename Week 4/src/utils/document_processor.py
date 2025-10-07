"""
Document Processing Module

Handles loading, chunking, and preprocessing of the EU AI Act PDF document.
"""

from typing import List
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document
from src.config import Config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentProcessor:
    """
    Processes PDF documents for the RAG system.

    This class handles:
    - Loading PDF documents
    - Splitting documents into chunks
    - Preprocessing text for optimal retrieval
    """

    def __init__(
        self,
        chunk_size: int = Config.CHUNK_SIZE,
        chunk_overlap: int = Config.CHUNK_OVERLAP
    ):
        """
        Initialize the document processor.

        Args:
            chunk_size: Maximum size of each text chunk
            chunk_overlap: Overlap between consecutive chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # Initialize text splitter with tiktoken encoding
        # This ensures consistent token-based chunking
        self.text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )

        logger.info(
            f"DocumentProcessor initialized with chunk_size={chunk_size}, "
            f"chunk_overlap={chunk_overlap}"
        )

    def load_pdf(self, pdf_path: Path) -> List[Document]:
        """
        Loads a PDF document from the specified path.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            List of Document objects, one per page

        Raises:
            FileNotFoundError: If the PDF file doesn't exist
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        logger.info(f"Loading PDF from {pdf_path}")

        # Load PDF using PyPDFLoader
        loader = PyPDFLoader(str(pdf_path))
        documents = loader.load()

        logger.info(f"✓ Loaded {len(documents)} pages from PDF")

        return documents

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Splits documents into smaller chunks for better retrieval.

        Args:
            documents: List of Document objects to split

        Returns:
            List of smaller Document chunks
        """
        logger.info(f"Splitting {len(documents)} documents into chunks")

        # Split documents using the text splitter
        chunks = self.text_splitter.split_documents(documents)

        logger.info(f"✓ Created {len(chunks)} document chunks")

        return chunks

    def process_document(self, pdf_path: Path) -> List[Document]:
        """
        Complete pipeline: load and chunk a PDF document.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            List of processed document chunks ready for embedding
        """
        logger.info("Starting document processing pipeline")

        # Load the PDF
        documents = self.load_pdf(pdf_path)

        # Split into chunks
        chunks = self.split_documents(documents)

        logger.info("✓ Document processing complete")

        return chunks

    def get_document_stats(self, chunks: List[Document]) -> dict:
        """
        Get statistics about the processed documents.

        Args:
            chunks: List of document chunks

        Returns:
            Dictionary with document statistics
        """
        total_chars = sum(len(chunk.page_content) for chunk in chunks)
        avg_chunk_size = total_chars / len(chunks) if chunks else 0

        pages = set()
        for chunk in chunks:
            if 'page' in chunk.metadata:
                pages.add(chunk.metadata['page'])

        return {
            "total_chunks": len(chunks),
            "total_characters": total_chars,
            "average_chunk_size": int(avg_chunk_size),
            "unique_pages": len(pages)
        }


def load_eu_ai_act() -> List[Document]:
    """
    Convenience function to load and process the EU AI Act PDF.

    Returns:
        List of processed document chunks

    Raises:
        FileNotFoundError: If the EU AI Act PDF is not found
    """
    processor = DocumentProcessor()
    return processor.process_document(Config.EU_AI_ACT_PDF)
