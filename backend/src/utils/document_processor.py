"""
Document processor utility.
This module contains functions for processing documents of various formats.
"""
import os
import re
import io
import numpy as np
from PIL import Image
from typing import List, Dict, Any, Tuple, Optional, Union
from pypdf import PdfReader
from docx import Document
import pandas as pd
from langchain.text_splitter import RecursiveCharacterTextSplitter
from .medical_image_classifier import MedicalImageClassifier

class DocumentProcessor:
    """Document processor class for handling various document formats."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize the document processor.

        Args:
            chunk_size: The size of each chunk in characters.
            chunk_overlap: The overlap between chunks in characters.
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        # Initialize the enhanced medical image classifier
        self.medical_image_classifier = MedicalImageClassifier()

    def process_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Process a file and return chunks with metadata.

        Args:
            file_path: The path to the file.

        Returns:
            A list of dictionaries containing chunks and metadata.
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        file_name = os.path.basename(file_path)

        if file_ext == '.pdf':
            return self._process_pdf(file_path, file_name)
        elif file_ext == '.txt':
            return self._process_text(file_path, file_name)
        elif file_ext in ['.docx', '.doc']:
            return self._process_docx(file_path, file_name)
        elif file_ext in ['.csv', '.xlsx', '.xls']:
            return self._process_tabular(file_path, file_name)
        elif file_ext in ['.png', '.jpg', '.jpeg', '.dcm', '.dicom', '.ima', '.img']:
            return self._process_image(file_path, file_name)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")

    def process_bytes(self, file_bytes: bytes, file_name: str) -> List[Dict[str, Any]]:
        """
        Process file bytes and return chunks with metadata.

        Args:
            file_bytes: The file content as bytes.
            file_name: The name of the file.

        Returns:
            A list of dictionaries containing chunks and metadata.
        """
        file_ext = os.path.splitext(file_name)[1].lower()

        if file_ext == '.pdf':
            return self._process_pdf_bytes(file_bytes, file_name)
        elif file_ext == '.txt':
            return self._process_text_bytes(file_bytes, file_name)
        elif file_ext in ['.docx', '.doc']:
            return self._process_docx_bytes(file_bytes, file_name)
        elif file_ext in ['.csv', '.xlsx', '.xls']:
            return self._process_tabular_bytes(file_bytes, file_name)
        elif file_ext in ['.png', '.jpg', '.jpeg', '.dcm', '.dicom', '.ima', '.img']:
            return self._process_image_bytes(file_bytes, file_name)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")

    def _process_pdf(self, file_path: str, file_name: str) -> List[Dict[str, Any]]:
        """Process a PDF file."""
        with open(file_path, 'rb') as f:
            return self._process_pdf_bytes(f.read(), file_name)

    def _process_pdf_bytes(self, file_bytes: bytes, file_name: str) -> List[Dict[str, Any]]:
        """Process PDF bytes."""
        chunks = []

        # Use pypdf for PDF processing
        try:
            from io import BytesIO
            from pypdf import PdfReader

            reader = PdfReader(BytesIO(file_bytes))

            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()
                if not text.strip():
                    continue

                # Create chunks from text
                text_chunks = self.text_splitter.split_text(text)

                for i, chunk in enumerate(text_chunks):
                    chunks.append({
                        "content": chunk,
                        "metadata": {
                            "source": file_name,
                            "page": page_num + 1,
                            "chunk": i + 1,
                            "total_chunks": len(text_chunks),
                            "content_type": "text"
                        }
                    })

        except Exception as e:
            logger.error(f"Error processing PDF with pypdf: {e}", exc_info=True)

        return chunks

    def _extract_images_from_pdf_page(self, page) -> List[bytes]:
        """Extract images from a PDF page."""
        # We're not using PyMuPDF, so we can't extract images from PDF pages
        # This is a simplified version that returns an empty list
        return []

    def _process_text(self, file_path: str, file_name: str) -> List[Dict[str, Any]]:
        """Process a text file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()

        return self._process_text_content(text, file_name)

    def _process_text_bytes(self, file_bytes: bytes, file_name: str) -> List[Dict[str, Any]]:
        """Process text file bytes."""
        text = file_bytes.decode('utf-8')
        return self._process_text_content(text, file_name)

    def _process_text_content(self, text: str, file_name: str) -> List[Dict[str, Any]]:
        """Process text content."""
        chunks = []
        text_chunks = self.text_splitter.split_text(text)

        for i, chunk in enumerate(text_chunks):
            chunks.append({
                "content": chunk,
                "metadata": {
                    "source": file_name,
                    "chunk": i + 1,
                    "total_chunks": len(text_chunks),
                    "content_type": "text"
                }
            })

        return chunks

    def _process_docx(self, file_path: str, file_name: str) -> List[Dict[str, Any]]:
        """Process a DOCX file."""
        with open(file_path, 'rb') as f:
            return self._process_docx_bytes(f.read(), file_name)

    def _process_docx_bytes(self, file_bytes: bytes, file_name: str) -> List[Dict[str, Any]]:
        """Process DOCX bytes."""
        doc = Document(io.BytesIO(file_bytes))
        text = "\n".join([para.text for para in doc.paragraphs])
        return self._process_text_content(text, file_name)

    def _process_tabular(self, file_path: str, file_name: str) -> List[Dict[str, Any]]:
        """Process a tabular file (CSV, Excel)."""
        with open(file_path, 'rb') as f:
            return self._process_tabular_bytes(f.read(), file_name)

    def _process_tabular_bytes(self, file_bytes: bytes, file_name: str) -> List[Dict[str, Any]]:
        """Process tabular file bytes."""
        file_ext = os.path.splitext(file_name)[1].lower()

        if file_ext == '.csv':
            df = pd.read_csv(io.BytesIO(file_bytes))
        else:  # Excel files
            df = pd.read_excel(io.BytesIO(file_bytes))

        # Convert DataFrame to text
        text = df.to_string(index=False)
        return self._process_text_content(text, file_name)

    def _process_image(self, file_path: str, file_name: str) -> List[Dict[str, Any]]:
        """Process an image file."""
        with open(file_path, 'rb') as f:
            return self._process_image_bytes(f.read(), file_name)

    def _process_image_bytes(self, file_bytes: bytes, file_name: str) -> List[Dict[str, Any]]:
        """Process image bytes with enhanced medical context using advanced medical image classifier."""
        # Use the enhanced medical image classifier
        image_analysis = self.medical_image_classifier.analyze_medical_image(file_bytes, file_name)

        # Create comprehensive medical description
        content_description = self.medical_image_classifier.create_medical_description(file_name, image_analysis)

        chunks = [{
            "content": content_description,
            "metadata": {
                "source": file_name,
                "content_type": "image",
                "image_data": file_bytes,
                "image_info": image_analysis,  # Now contains comprehensive analysis
                "medical_context": True,
                "is_dicom": image_analysis.get('is_dicom', False),
                "medical_type": image_analysis.get('medical_type', 'medical_image')
            }
        }]

        return chunks
