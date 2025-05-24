"""
Medical embedding service.
This module contains functions for generating embeddings for medical text and images.
"""
import os
import numpy as np
from typing import List, Dict, Any, Union, Optional
from sentence_transformers import SentenceTransformer
import io
from ..config import get_config

config = get_config()

class MedicalEmbeddingService:
    """Service for generating embeddings for medical text and images."""

    _instance = None
    _initialized = False
    _lock = None

    def __new__(cls):
        """Implement singleton pattern to prevent duplicate model loading."""
        if cls._instance is None:
            import threading
            if cls._lock is None:
                cls._lock = threading.Lock()

            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(MedicalEmbeddingService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the embedding service with appropriate models."""
        # Only initialize once per process
        if MedicalEmbeddingService._initialized:
            return

        print("Initializing MedicalEmbeddingService singleton...")
        self.text_model_name = getattr(config, 'MEDICAL_TEXT_EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
        self.image_model_name = getattr(config, 'MEDICAL_IMAGE_EMBEDDING_MODEL', '')
        self.embedding_model = getattr(config, 'EMBEDDING_MODEL', 'all-MiniLM-L6-v2')

        # Initialize text embedding model
        self._init_text_model()

        # Initialize image embedding model if needed
        self._init_image_model()

        MedicalEmbeddingService._initialized = True
        print("MedicalEmbeddingService singleton initialized successfully")

    def _init_text_model(self):
        """Initialize the text embedding model."""
        try:
            # Try to use HuggingFace transformers for medical models
            try:
                import torch
                from transformers import AutoTokenizer, AutoModel

                self.text_tokenizer = AutoTokenizer.from_pretrained(self.text_model_name)
                self.text_model = AutoModel.from_pretrained(self.text_model_name)
                self.use_huggingface = True
                print(f"Successfully loaded HuggingFace model: {self.text_model_name}")
            except Exception as e:
                print(f"Failed to load HuggingFace model: {e}")
                print("Falling back to SentenceTransformer model")
                # Fall back to SentenceTransformer
                self.text_model = SentenceTransformer(self.embedding_model)
                self.use_huggingface = False
        except Exception as e:
            print(f"Failed to initialize any text embedding model: {e}")
            print("Using dummy embeddings - SYSTEM WILL NOT WORK PROPERLY")
            self.text_model = None
            self.use_huggingface = False

    def _init_image_model(self):
        """Initialize the image embedding model."""
        self.has_image_model = False
        self.image_processor = None
        self.image_model = None

        if not self.image_model_name:
            print("No image model specified, skipping image model initialization")
            return

        try:
            # Try to load medical image model
            try:
                import torch
                from transformers import AutoProcessor, AutoModel

                self.image_processor = AutoProcessor.from_pretrained(
                    self.image_model_name,
                    trust_remote_code=True
                )
                self.image_model = AutoModel.from_pretrained(
                    self.image_model_name,
                    trust_remote_code=True
                )
                self.has_image_model = True
                print(f"Successfully loaded image model: {self.image_model_name}")
            except Exception as e:
                print(f"Failed to load specified image model: {e}")
                try:
                    # Try to use CLIP as fallback
                    from transformers import CLIPProcessor, CLIPModel
                    self.image_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
                    self.image_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
                    self.has_image_model = True
                    print("Successfully loaded CLIP model as fallback")
                except Exception as e2:
                    print(f"Failed to load CLIP model: {e2}")
        except Exception as e:
            print(f"Failed to initialize any image embedding model: {e}")

    def get_text_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for text.

        Args:
            text: The text to embed.

        Returns:
            The embedding as a numpy array.
        """
        if self.text_model is None:
            # Return a dummy embedding if no model is available
            return np.zeros(768, dtype=np.float32)

        try:
            if self.use_huggingface:
                # Using HuggingFace model (BioClinicalBERT)
                import torch

                inputs = self.text_tokenizer(text, return_tensors="pt",
                                            padding=True, truncation=True, max_length=512)
                with torch.no_grad():
                    outputs = self.text_model(**inputs)

                # Use CLS token embedding or mean pooling
                embeddings = outputs.last_hidden_state[:, 0, :].numpy()  # CLS token
                return embeddings[0]  # Return the first embedding (batch size 1)
            else:
                # Using SentenceTransformer
                return self.text_model.encode(text)
        except Exception as e:
            print(f"Error generating text embedding: {e}")
            # Return a dummy embedding if embedding generation fails
            return np.zeros(768, dtype=np.float32)

    def get_image_embedding(self, image_data: bytes) -> Optional[np.ndarray]:
        """
        Generate embedding for an image.

        Args:
            image_data: The image data as bytes.

        Returns:
            The embedding as a numpy array, or None if image processing fails.
        """
        if not self.has_image_model:
            return None

        try:
            # Import PIL only when needed
            from PIL import Image

            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))

            # Process image with the model
            import torch
            inputs = self.image_processor(images=image, return_tensors="pt")
            with torch.no_grad():
                outputs = self.image_model(**inputs)

            # Get image features
            if hasattr(outputs, 'image_embeds'):
                # CLIP-like model
                image_embedding = outputs.image_embeds.numpy()
            elif hasattr(outputs, 'pooler_output'):
                # Vision transformer with pooler
                image_embedding = outputs.pooler_output.numpy()
            else:
                # Last hidden state, use mean pooling
                image_embedding = outputs.last_hidden_state.mean(dim=1).numpy()

            return image_embedding[0]  # Return the first embedding (batch size 1)
        except Exception as e:
            print(f"Error generating image embedding: {e}")
            return None

    def get_embeddings_batch(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a batch of texts.

        Args:
            texts: List of texts to embed.

        Returns:
            Array of embeddings.
        """
        if self.text_model is None:
            # Return dummy embeddings if no model is available
            return np.zeros((len(texts), 768), dtype=np.float32)

        try:
            if self.use_huggingface:
                # Using HuggingFace model (BioClinicalBERT)
                embeddings = []
                for text in texts:
                    embeddings.append(self.get_text_embedding(text))
                return np.array(embeddings)
            else:
                # Using SentenceTransformer (more efficient batch processing)
                return self.text_model.encode(texts)
        except Exception as e:
            print(f"Error generating batch embeddings: {e}")
            # Return dummy embeddings if embedding generation fails
            return np.zeros((len(texts), 768), dtype=np.float32)

    def embed_document_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate embeddings for document chunks.

        Args:
            chunks: List of document chunks with content and metadata.

        Returns:
            List of chunks with embeddings added.
        """
        for chunk in chunks:
            try:
                content_type = chunk["metadata"].get("content_type", "text")

                if content_type == "text":
                    # Generate text embedding
                    chunk["embedding"] = self.get_text_embedding(chunk["content"])
                elif content_type == "image" and "image_data" in chunk["metadata"]:
                    # Generate image embedding if possible
                    image_embedding = self.get_image_embedding(chunk["metadata"]["image_data"])
                    if image_embedding is not None:
                        chunk["embedding"] = image_embedding
                        # Keep the image data for now
                        # In production, you might want to remove it to save space:
                        # chunk["metadata"].pop("image_data", None)
                    else:
                        # If image embedding fails, use a text description embedding instead
                        chunk["embedding"] = self.get_text_embedding(chunk["content"])
                else:
                    # Default to text embedding for unknown content types
                    chunk["embedding"] = self.get_text_embedding(chunk["content"])
            except Exception as e:
                print(f"Error embedding chunk: {e}")
                # Provide a dummy embedding to avoid breaking the pipeline
                chunk["embedding"] = np.zeros(768, dtype=np.float32)

        return chunks
