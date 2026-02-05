"""
Chunker module.
Splits large documents into smaller, retrieveable chunks.
"""

from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk_text(documents: List[Document], chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Document]:
    """
    Splits documents into smaller chunks using RecursiveCharacterTextSplitter.

    Args:
        documents (List[Document]): The raw documents to chunk.
        chunk_size (int): The target size of each chunk (in characters).
        chunk_overlap (int): The number of overlapping characters between chunks.

    Returns:
        List[Document]: List of chunked documents.
    """
    print(f"Splitting {len(documents)} documents...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    
    chunks = text_splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks.")
    return chunks
