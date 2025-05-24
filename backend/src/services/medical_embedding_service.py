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
        """Initialize the image embedding model with medical-specific handling."""
        self.has_image_model = False
        self.image_processor = None
        self.image_model = None
        self.is_medical_model = False
        self.is_clip_model = False

        if not self.image_model_name:
            print("No image model specified, skipping image model initialization")
            return

        try:
            # Try to load medical image model first
            try:
                import torch
                from transformers import AutoProcessor, AutoModel

                print(f"Attempting to load medical image model: {self.image_model_name}")
                self.image_processor = AutoProcessor.from_pretrained(
                    self.image_model_name,
                    trust_remote_code=True
                )
                self.image_model = AutoModel.from_pretrained(
                    self.image_model_name,
                    trust_remote_code=True
                )
                self.has_image_model = True
                self.is_medical_model = True
                print(f"✅ Successfully loaded medical image model: {self.image_model_name}")
            except Exception as e:
                print(f"❌ Failed to load specified medical image model: {e}")
                print("Attempting to load CLIP as fallback...")
                try:
                    # Try to use CLIP as fallback
                    from transformers import CLIPProcessor, CLIPModel
                    self.image_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
                    self.image_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
                    self.has_image_model = True
                    self.is_clip_model = True
                    self.image_model_name = "openai/clip-vit-base-patch32"  # Update model name
                    print("✅ Successfully loaded CLIP model as fallback")
                except Exception as e2:
                    print(f"❌ Failed to load CLIP model: {e2}")
                    print("⚠️  No image embedding model available - images will use text embeddings")
        except Exception as e:
            print(f"❌ Failed to initialize any image embedding model: {e}")
            print("⚠️  Image processing will fall back to text-based embeddings")

    def _generate_medical_context_text(self, image_data: bytes, image_analysis: Dict[str, Any] = None) -> str:
        """
        Generate appropriate medical context text for image embedding using enhanced analysis.

        Args:
            image_data: The image data as bytes.
            image_analysis: Optional comprehensive medical image analysis from MedicalImageClassifier.

        Returns:
            Medical context text appropriate for the image.
        """
        try:
            # Use enhanced medical analysis if available
            if image_analysis:
                return self._generate_enhanced_medical_context(image_analysis)

            # Fallback to basic analysis
            return self._generate_basic_medical_context(image_data)

        except Exception as e:
            print(f"Error generating medical context: {e}")
            # Fallback to generic medical context
            return "medical image for clinical diagnostic evaluation and healthcare analysis"

    def _generate_enhanced_medical_context(self, image_analysis: Dict[str, Any]) -> str:
        """Generate medical context using comprehensive image analysis."""
        context_parts = []

        # Use DICOM information if available
        if image_analysis.get('is_dicom', False):
            modality = image_analysis.get('modality', 'Unknown')
            body_part = image_analysis.get('body_part_examined', '')

            # Add DICOM-specific context
            context_parts.append(f"DICOM {modality} medical image")

            if body_part and body_part != 'Unknown':
                context_parts.append(f"of {body_part}")

            # Add study information if available
            study_desc = image_analysis.get('study_description', '')
            if study_desc:
                context_parts.append(f"for {study_desc}")

            # Add series information
            series_desc = image_analysis.get('series_description', '')
            if series_desc:
                context_parts.append(f"series {series_desc}")
        else:
            # Use enhanced medical type classification
            medical_type = image_analysis.get('medical_type', 'medical_image')
            context_parts.append(f"{medical_type.replace('_', ' ')}")

            # Add filename-based medical indicators
            medical_context = image_analysis.get('medical_context', {})
            filename_indicators = medical_context.get('filename_indicators', [])
            if filename_indicators:
                context_parts.append(f"with indicators: {', '.join(filename_indicators)}")

        # Add image characteristics
        if 'width' in image_analysis and 'height' in image_analysis:
            dimensions = f"{image_analysis['width']}x{image_analysis['height']}"
            context_parts.append(f"resolution {dimensions}")

        # Add medical relevance information
        medical_context = image_analysis.get('medical_context', {})
        relevance_score = medical_context.get('medical_relevance_score', 0)
        if relevance_score > 0.7:
            context_parts.append("high medical relevance")
        elif relevance_score > 0.5:
            context_parts.append("moderate medical relevance")

        # Add standard medical descriptors
        context_parts.extend([
            "for clinical diagnostic evaluation",
            "medical documentation",
            "healthcare analysis"
        ])

        return " ".join(context_parts)

    def _generate_basic_medical_context(self, image_data: bytes) -> str:
        """Generate basic medical context when enhanced analysis is not available."""
        try:
            from PIL import Image
            import io

            # Load image to analyze basic properties
            image = Image.open(io.BytesIO(image_data))
            width, height = image.size
            mode = image.mode

            # Determine image characteristics
            is_grayscale = mode in ['L', 'LA']
            is_large = width > 1000 or height > 1000
            aspect_ratio = width / height

            # Generate context based on image characteristics
            context_parts = []

            # Base medical image description
            if is_grayscale:
                context_parts.append("medical radiological image")
                if aspect_ratio > 1.2:
                    context_parts.append("chest X-ray")
                elif 0.8 <= aspect_ratio <= 1.2:
                    context_parts.append("medical scan")
                else:
                    context_parts.append("medical imaging study")
            else:
                context_parts.append("medical clinical image")
                if is_large:
                    context_parts.append("high resolution medical photograph")
                else:
                    context_parts.append("clinical documentation image")

            # Add general medical descriptors
            context_parts.extend([
                "for diagnostic evaluation",
                "clinical assessment",
                "medical documentation",
                "healthcare analysis"
            ])

            # Create comprehensive medical context
            medical_context = " ".join(context_parts)

            return medical_context

        except Exception as e:
            print(f"Error generating basic medical context: {e}")
            # Fallback to generic medical context
            return "medical image for clinical diagnostic evaluation and healthcare analysis"

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

    def get_image_embedding(self, image_data: bytes, image_analysis: Dict[str, Any] = None) -> Optional[np.ndarray]:
        """
        Generate embedding for an image using enhanced medical analysis.

        Args:
            image_data: The image data as bytes.
            image_analysis: Optional comprehensive medical image analysis from MedicalImageClassifier.

        Returns:
            The embedding as a numpy array, or None if image processing fails.
        """
        print(f"=== GET IMAGE EMBEDDING ===")
        print(f"Has image model: {self.has_image_model}")
        print(f"Image data size: {len(image_data)} bytes")

        if not self.has_image_model:
            print("No image model available, returning None")
            return None

        try:
            # Import PIL only when needed
            from PIL import Image

            # Convert bytes to PIL Image
            print("Converting bytes to PIL Image...")
            image = Image.open(io.BytesIO(image_data))
            print(f"Image loaded: {image.size}, mode: {image.mode}")

            # Process image with the model
            print("Processing image with model...")
            import torch

            # Handle different model types with appropriate inputs
            if self.is_medical_model and "BiomedVLP" in self.image_model_name:
                # BiomedVLP models require both text and image for optimal performance
                print("Using BiomedVLP medical model - providing medical context text")

                # Generate appropriate medical context text based on enhanced image analysis
                medical_context = self._generate_medical_context_text(image_data, image_analysis)
                print(f"Enhanced medical context: {medical_context}")

                inputs = self.image_processor(
                    text=[medical_context],
                    images=image,
                    return_tensors="pt",
                    padding=True
                )
            elif self.is_clip_model:
                # CLIP models work with image-only input
                print("Using CLIP model for medical image embedding")
                inputs = self.image_processor(images=image, return_tensors="pt")
            else:
                # Generic fallback for other models
                print("Using generic image model")
                try:
                    # Try image-only first
                    inputs = self.image_processor(images=image, return_tensors="pt")
                except:
                    # If that fails, try with enhanced medical context text
                    medical_context = self._generate_medical_context_text(image_data, image_analysis)
                    inputs = self.image_processor(
                        text=[medical_context],
                        images=image,
                        return_tensors="pt",
                        padding=True
                    )

            with torch.no_grad():
                outputs = self.image_model(**inputs)

            # Get image features
            print("Extracting image features...")
            if hasattr(outputs, 'image_embeds'):
                # CLIP-like model
                print("Using image_embeds from CLIP-like model")
                image_embedding = outputs.image_embeds.numpy()
            elif hasattr(outputs, 'pooler_output'):
                # Vision transformer with pooler
                print("Using pooler_output from vision transformer")
                image_embedding = outputs.pooler_output.numpy()
            else:
                # Last hidden state, use mean pooling
                print("Using mean pooling of last_hidden_state")
                image_embedding = outputs.last_hidden_state.mean(dim=1).numpy()

            print(f"Generated image embedding with shape: {image_embedding.shape}")
            return image_embedding[0]  # Return the first embedding (batch size 1)
        except Exception as e:
            print(f"Error generating image embedding: {e}")
            import traceback
            traceback.print_exc()
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
        print(f"=== EMBEDDING DOCUMENT CHUNKS ===")
        print(f"Processing {len(chunks)} chunks")

        for i, chunk in enumerate(chunks):
            try:
                content_type = chunk["metadata"].get("content_type", "text")
                print(f"Chunk {i+1}: content_type = {content_type}")

                if content_type == "text":
                    # Generate text embedding
                    chunk["embedding"] = self.get_text_embedding(chunk["content"])
                elif content_type == "image" and "image_data" in chunk["metadata"]:
                    # Generate image embedding using enhanced medical analysis
                    print(f"Processing image chunk with {len(chunk['metadata']['image_data'])} bytes")

                    # Get enhanced medical image analysis if available
                    image_analysis = chunk["metadata"].get("image_info", None)
                    if image_analysis:
                        print(f"Using enhanced medical analysis: {image_analysis.get('medical_type', 'unknown')}")

                    image_embedding = self.get_image_embedding(chunk["metadata"]["image_data"], image_analysis)
                    print(f"Image embedding result: {image_embedding is not None}")
                    if image_embedding is not None:
                        print(f"Image embedding shape: {image_embedding.shape}")
                        chunk["embedding"] = image_embedding
                        # Keep the image data for now
                        # In production, you might want to remove it to save space:
                        # chunk["metadata"].pop("image_data", None)
                    else:
                        # If image embedding fails, use a text description embedding instead
                        print("Image embedding failed, using text embedding fallback")
                        chunk["embedding"] = self.get_text_embedding(chunk["content"])
                else:
                    # Default to text embedding for unknown content types
                    print(f"Using text embedding for content_type: {content_type}")
                    chunk["embedding"] = self.get_text_embedding(chunk["content"])

                print(f"Final embedding shape for chunk {i+1}: {chunk['embedding'].shape}")
            except Exception as e:
                print(f"Error embedding chunk {i+1}: {e}")
                import traceback
                traceback.print_exc()
                # Provide a dummy embedding to avoid breaking the pipeline
                chunk["embedding"] = np.zeros(768, dtype=np.float32)

        print(f"Completed embedding {len(chunks)} chunks")
        return chunks
