"""
PDF ingestion pipeline for the Puja AI chatbot system.
Handles PDF processing, text extraction, cleaning, chunking, and ChromaDB storage.
"""

import os
import sys
import hashlib
import argparse
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
import re

import pdfplumber
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

from chroma_client import create_chroma_client
from embeddings_helper import generate_embeddings

# Load environment variables
load_dotenv()

class PDFIngestor:
    """Handles PDF ingestion into ChromaDB with comprehensive text processing."""
    
    def __init__(self, pdf_dir: str = "./pdfs", force: bool = False):
        """
        Initialize PDF ingestor.
        
        Args:
            pdf_dir: Directory containing PDF files
            force: Force re-indexing of already processed PDFs
        """
        self.pdf_dir = Path(pdf_dir)
        self.force = force
        
        # Initialize ChromaDB client
        self.chroma_client = create_chroma_client()
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""],
            length_function=len
        )
        
        # Processed files tracking
        self.processed_files_path = Path("./data/processed_files.json")
        self.processed_files = self.load_processed_files()
        
        # Statistics
        self.stats = {
            "num_pdfs": 0,
            "total_chunks": 0,
            "skipped_pdfs": 0,
            "errors": []
        }
    
    def load_processed_files(self) -> Dict[str, str]:
        """Load the record of previously processed files with their checksums."""
        try:
            if self.processed_files_path.exists():
                with open(self.processed_files_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load processed files record: {e}")
        
        return {}
    
    def save_processed_files(self):
        """Save the record of processed files."""
        try:
            os.makedirs(self.processed_files_path.parent, exist_ok=True)
            with open(self.processed_files_path, 'w') as f:
                json.dump(self.processed_files, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save processed files record: {e}")
    
    def calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate MD5 checksum of a file."""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            print(f"Error calculating checksum for {file_path}: {e}")
            return ""
    
    def should_process_file(self, file_path: Path) -> bool:
        """Check if a file should be processed (new or changed)."""
        if self.force:
            return True
        
        file_str = str(file_path)
        current_checksum = self.calculate_file_checksum(file_path)
        
        if not current_checksum:
            return False
        
        stored_checksum = self.processed_files.get(file_str, "")
        return current_checksum != stored_checksum
    
    def extract_text_with_pdfplumber(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Extract text from PDF using pdfplumber with page-by-page processing.
        
        Returns:
            List of page dictionaries with text and metadata
        """
        pages_data = []
        
        try:
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    try:
                        text = page.extract_text()
                        if text and text.strip():
                            pages_data.append({
                                "text": text,
                                "page": page_num,
                                "extraction_method": "pdfplumber"
                            })
                    except Exception as e:
                        print(f"Error extracting page {page_num} from {file_path}: {e}")
                        continue
        
        except Exception as e:
            print(f"Error opening PDF with pdfplumber {file_path}: {e}")
            return []
        
        return pages_data
    
    def extract_text_with_pypdf2(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Fallback text extraction using PyPDF2.
        
        Returns:
            List of page dictionaries with text and metadata
        """
        pages_data = []
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    try:
                        text = page.extract_text()
                        if text and text.strip():
                            pages_data.append({
                                "text": text,
                                "page": page_num,
                                "extraction_method": "pypdf2"
                            })
                    except Exception as e:
                        print(f"Error extracting page {page_num} from {file_path}: {e}")
                        continue
        
        except Exception as e:
            print(f"Error opening PDF with PyPDF2 {file_path}: {e}")
            return []
        
        return pages_data
    
    def clean_text(self, text: str) -> str:
        """
        Clean extracted text by removing headers/footers, normalizing whitespace.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Split into lines for processing
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Skip lines that are just page numbers
            if re.match(r'^\d+$', line):
                continue
            
            # Skip very short lines that might be headers/footers
            if len(line) < 3:
                continue
            
            # Skip lines with only special characters
            if re.match(r'^[^\w\s]*$', line):
                continue
            
            cleaned_lines.append(line)
        
        # Join lines back
        cleaned_text = '\n'.join(cleaned_lines)
        
        # Normalize whitespace
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        cleaned_text = re.sub(r'\n\s*\n', '\n\n', cleaned_text)
        
        return cleaned_text.strip()
    
    def detect_repeated_headers_footers(self, pages_data: List[Dict[str, Any]]) -> List[str]:
        """
        Detect repeated headers/footers across pages.
        
        Returns:
            List of repeated text patterns to remove
        """
        if len(pages_data) < 3:
            return []
        
        # Extract first and last lines from each page
        first_lines = []
        last_lines = []
        
        for page_data in pages_data:
            lines = page_data["text"].split('\n')
            lines = [line.strip() for line in lines if line.strip()]
            
            if len(lines) > 0:
                first_lines.append(lines[0])
            if len(lines) > 1:
                last_lines.append(lines[-1])
        
        repeated_patterns = []
        
        # Check for repeated first lines (headers)
        if len(set(first_lines)) < len(first_lines) * 0.3:  # If 70%+ are the same
            most_common_first = max(set(first_lines), key=first_lines.count)
            if first_lines.count(most_common_first) >= len(pages_data) * 0.5:
                repeated_patterns.append(most_common_first)
        
        # Check for repeated last lines (footers)
        if len(set(last_lines)) < len(last_lines) * 0.3:
            most_common_last = max(set(last_lines), key=last_lines.count)
            if last_lines.count(most_common_last) >= len(pages_data) * 0.5:
                repeated_patterns.append(most_common_last)
        
        return repeated_patterns
    
    def remove_headers_footers(self, text: str, repeated_patterns: List[str]) -> str:
        """Remove detected headers/footers from text."""
        if not repeated_patterns:
            return text
        
        lines = text.split('\n')
        filtered_lines = []
        
        for line in lines:
            line_stripped = line.strip()
            should_keep = True
            
            for pattern in repeated_patterns:
                if line_stripped == pattern.strip():
                    should_keep = False
                    break
            
            if should_keep:
                filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
    
    def extract_and_process_pdf(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Extract and process text from a single PDF.
        
        Returns:
            List of processed page data
        """
        print(f"Processing: {file_path.name}")
        
        # Try pdfplumber first, fallback to PyPDF2
        pages_data = self.extract_text_with_pdfplumber(file_path)
        
        if not pages_data:
            print(f"  Fallback to PyPDF2 for {file_path.name}")
            pages_data = self.extract_text_with_pypdf2(file_path)
        
        if not pages_data:
            print(f"  No text extracted from {file_path.name}")
            return []
        
        print(f"  Extracted {len(pages_data)} pages")
        
        # Detect repeated headers/footers
        repeated_patterns = self.detect_repeated_headers_footers(pages_data)
        if repeated_patterns:
            print(f"  Detected {len(repeated_patterns)} repeated patterns")
        
        # Clean each page
        for page_data in pages_data:
            # Remove headers/footers
            page_data["text"] = self.remove_headers_footers(page_data["text"], repeated_patterns)
            
            # Clean text
            page_data["text"] = self.clean_text(page_data["text"])
        
        # Filter out pages with insufficient text
        pages_data = [page for page in pages_data if len(page["text"]) > 50]
        
        print(f"  Cleaned to {len(pages_data)} usable pages")
        
        return pages_data
    
    def create_chunks(self, pages_data: List[Dict[str, Any]], book_title: str) -> List[Dict[str, Any]]:
        """
        Create chunks from processed pages with metadata.
        
        Returns:
            List of chunk documents ready for ChromaDB
        """
        chunks = []
        
        for page_data in pages_data:
            page_text = page_data["text"]
            page_num = page_data["page"]
            
            if not page_text or len(page_text.strip()) < 50:
                continue
            
            # Split text into chunks
            text_chunks = self.text_splitter.split_text(page_text)
            
            for chunk_idx, chunk_text in enumerate(text_chunks):
                if len(chunk_text.strip()) < 30:  # Skip very small chunks
                    continue
                
                chunk_id = str(uuid.uuid4())
                
                chunk_doc = {
                    "page_content": chunk_text.strip(),
                    "metadata": {
                        "book_title": book_title,
                        "page": page_num,
                        "chunk_id": chunk_id,
                        "chunk_index": chunk_idx,
                        "source_file": book_title,
                        "extraction_method": page_data.get("extraction_method", "unknown")
                    }
                }
                
                chunks.append(chunk_doc)
        
        return chunks
    
    def process_single_pdf(self, file_path: Path) -> int:
        """
        Process a single PDF file.
        
        Returns:
            Number of chunks created
        """
        # Check if we should process this file
        if not self.should_process_file(file_path):
            print(f"Skipping {file_path.name} (already processed)")
            self.stats["skipped_pdfs"] += 1
            return 0
        
        try:
            # Extract and process text
            pages_data = self.extract_and_process_pdf(file_path)
            
            if not pages_data:
                self.stats["errors"].append(f"No text extracted from {file_path.name}")
                return 0
            
            # Create book title from filename
            book_title = file_path.stem.replace('_', ' ').replace('-', ' ').title()
            
            # Create chunks
            chunks = self.create_chunks(pages_data, book_title)
            
            if not chunks:
                self.stats["errors"].append(f"No chunks created from {file_path.name}")
                return 0
            
            print(f"  Created {len(chunks)} chunks")
            
            # Add to ChromaDB
            success = self.chroma_client.add_documents(chunks)
            
            if success:
                # Update processed files record
                checksum = self.calculate_file_checksum(file_path)
                self.processed_files[str(file_path)] = checksum
                
                self.stats["num_pdfs"] += 1
                self.stats["total_chunks"] += len(chunks)
                
                print(f"  Successfully indexed {file_path.name}")
                return len(chunks)
            else:
                self.stats["errors"].append(f"Failed to add {file_path.name} to ChromaDB")
                return 0
                
        except Exception as e:
            error_msg = f"Error processing {file_path.name}: {str(e)}"
            print(f"  {error_msg}")
            self.stats["errors"].append(error_msg)
            return 0
    
    def process_all_pdfs(self) -> Dict[str, Any]:
        """
        Process all PDFs in the specified directory.
        
        Returns:
            Processing statistics
        """
        if not self.pdf_dir.exists():
            print(f"Error: PDF directory {self.pdf_dir} does not exist")
            return self.stats
        
        # Find all PDF files
        pdf_files = list(self.pdf_dir.glob("*.pdf"))
        
        if not pdf_files:
            print(f"No PDF files found in {self.pdf_dir}")
            return self.stats
        
        print(f"Found {len(pdf_files)} PDF files")
        print(f"Force reindex: {self.force}")
        print("-" * 50)
        
        # Process each PDF
        for pdf_file in pdf_files:
            chunks_created = self.process_single_pdf(pdf_file)
            
        # Save processed files record
        self.save_processed_files()
        
        # Calculate averages
        if self.stats["num_pdfs"] > 0:
            self.stats["average_chunks_per_pdf"] = self.stats["total_chunks"] / self.stats["num_pdfs"]
        else:
            self.stats["average_chunks_per_pdf"] = 0
        
        return self.stats
    
    def print_summary(self):
        """Print processing summary."""
        print("\n" + "=" * 50)
        print("INGESTION SUMMARY")
        print("=" * 50)
        print(f"PDFs processed: {self.stats['num_pdfs']}")
        print(f"PDFs skipped: {self.stats['skipped_pdfs']}")
        print(f"Total chunks created: {self.stats['total_chunks']}")
        print(f"Average chunks per PDF: {self.stats['average_chunks_per_pdf']:.1f}")
        
        if self.stats["errors"]:
            print(f"\nErrors ({len(self.stats['errors'])}):")
            for error in self.stats["errors"]:
                print(f"  - {error}")
        
        print("\nChromaDB Collection Info:")
        collection_info = self.chroma_client.get_collection_info()
        for key, value in collection_info.items():
            print(f"  {key}: {value}")

def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description="Ingest PDFs into ChromaDB for Puja AI")
    parser.add_argument(
        "--pdf_dir",
        type=str,
        default="./pdfs",
        help="Directory containing PDF files (default: ./pdfs)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-indexing of already processed PDFs"
    )
    
    args = parser.parse_args()
    
    # Create ingestor and process files
    ingestor = PDFIngestor(pdf_dir=args.pdf_dir, force=args.force)
    stats = ingestor.process_all_pdfs()
    ingestor.print_summary()
    
    # Exit with appropriate code
    if stats["errors"]:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
