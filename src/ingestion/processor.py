"""
Data Processing module.
Handles loading, metadata injection, and pre-processing for different knowledge layers (FAQ, Policy, Web).
"""

import csv
import os
from typing import List, Tuple
from langchain_core.documents import Document
from src.ingestion.chunker import chunk_text
from src.config import DATA_DIR

def load_csv_as_documents(file_path: str) -> List[Document]:
    """
    Loads a CSV file and converts each row into a Document.
    
    Args:
        file_path (str): Path to the CSV file.
        
    Returns:
        List[Document]: List of documents with metadata.
    """
    documents = []
    try:
        with open(file_path, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # FAQ format: Q: <question> A: <answer>
                content = f"Q: {row['question']}\nA: {row['answer']}"
                
                # Metadata from columns
                metadata = {
                    "category": row.get("category", "general"),
                    "risk_level": row.get("risk_level", "low"),
                    "intent": row.get("intent", "informational"),
                    "answer_type": row.get("answer_type", "factual"),
                    "last_verified": "2024-05", # Default verification date
                    "source": "decision_faq"
                }
                
                documents.append(Document(page_content=content, metadata=metadata))
    except Exception as e:
        print(f"Error loading CSV {file_path}: {e}")
    return documents

def load_markdown_as_documents(file_path: str) -> List[Document]:
    """
    Loads a Markdown file and splits it by H2 headers (##).

    Args:
        file_path (str): Path to the Markdown file.

    Returns:
        List[Document]: List of section-based documents.
    """
    documents = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Simple splitting by "## "
        sections = text.split("\n## ")
        
        for section in sections:
            if not section.strip():
                continue
                
            lines = section.split("\n")
            title = lines[0].strip()
            content = "\n".join(lines[1:]).strip()
            
            metadata = {
                "source": "policy_documents",
                "last_verified": "2024-05"
            }
            
            # Simple extraction of metadata fields
            final_content_lines = []
            for line in content.split("\n"):
                if "**Category:**" in line:
                    metadata["category"] = line.split(":", 1)[1].strip().lower()
                elif "**Risk Level:**" in line:
                    metadata["risk_level"] = line.split(":", 1)[1].strip().lower()
                elif "**Intent:**" in line:
                    metadata["intent"] = line.split(":", 1)[1].strip().lower()
                elif "**Answer Type:**" in line:
                    metadata["answer_type"] = line.split(":", 1)[1].strip().lower()
                else:
                    final_content_lines.append(line)
            
            clean_content = f"Policy: {title}\n" + "\n".join(final_content_lines).strip()
            
            documents.append(Document(page_content=clean_content, metadata=metadata))
            
    except Exception as e:
        print(f"Error loading Markdown {file_path}: {e}")
    return documents

def process_decision_faq() -> List[Document]:
    """
    Processes the Decision FAQ CSV.

    Returns:
        List[Document]: Chunked documents.
    """
    file_path = os.path.join(DATA_DIR, "seed_content", "decision_faq.csv")
    print(f"Processing Decision FAQ from {file_path}...")
    
    docs = load_csv_as_documents(file_path)
    
    # Requirement: Chunk Size ~50-120 tokens (~200-500 chars)
    chunks = chunk_text(docs, chunk_size=200, chunk_overlap=20)
    
    return chunks

def process_policy_documents() -> List[Document]:
    """
    Processes Policy Markdown files.

    Returns:
        List[Document]: Chunked documents.
    """
    file_path = os.path.join(DATA_DIR, "seed_content", "policy_documents.md")
    print(f"Processing Policy Documents from {file_path}...")
    
    docs = load_markdown_as_documents(file_path)
    # Policy docs need to be retrieval friendly.
    chunks = chunk_text(docs, chunk_size=800, chunk_overlap=100) 
    return chunks

def process_web_content(scraped_docs: List[Document]) -> Tuple[List[Document], List[Document]]:
    """
    Processes scraped web content.
    Classifies pages into Program vs Trust based on rules.

    Args:
        scraped_docs (List[Document]): Raw scraped pages.

    Returns:
        Tuple[List[Document], List[Document]]: (program_chunks, trust_chunks)
    """
    program_docs = []
    trust_docs = []
    
    for doc in scraped_docs:
        url = doc.metadata.get("source", "")
        
        # Enforce metadata schema
        doc.metadata["last_verified"] = "2024-05"
        
        # Classification logic
        if "about-us" in url or "reviews" in url.lower():
            doc.metadata["category"] = "credibility"
            doc.metadata["intent"] = "decision" # verification
            trust_docs.append(doc)
        else:
            doc.metadata["category"] = "program" # broad default for scraped content
            doc.metadata["intent"] = "informational"
            doc.metadata["risk_level"] = "low"
            doc.metadata["answer_type"] = "factual"
            program_docs.append(doc)
            
    # Chunking
    # Program: <300 tokens (~1200 chars) for granular retrieval
    program_chunks = chunk_text(program_docs, chunk_size=1000, chunk_overlap=150)
    
    # Trust: Standard chunks
    trust_chunks = chunk_text(trust_docs, chunk_size=1000, chunk_overlap=150)
    
    return program_chunks, trust_chunks
