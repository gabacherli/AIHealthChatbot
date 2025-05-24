"""
Enhanced medical image classification using DICOM standards and medical AI models.
"""

import io
import os
import logging
from typing import Dict, Any, Optional, Tuple, List
from PIL import Image
import numpy as np

# Set up logging
logger = logging.getLogger(__name__)


class MedicalImageClassifier:
    """
    Advanced medical image classifier that uses DICOM metadata and medical AI models
    for accurate medical image type identification and metadata extraction.
    """

    def __init__(self):
        """Initialize the medical image classifier."""
        self.dicom_available = self._check_dicom_availability()
        self.simpleitk_available = self._check_simpleitk_availability()
        self.medmnist_available = self._check_medmnist_availability()

        # DICOM modality mappings
        self.dicom_modalities = {
            'CR': 'computed_radiography',
            'CT': 'computed_tomography',
            'MR': 'magnetic_resonance',
            'NM': 'nuclear_medicine',
            'US': 'ultrasound',
            'XA': 'x_ray_angiography',
            'RF': 'radiofluoroscopy',
            'DX': 'digital_radiography',
            'MG': 'mammography',
            'IO': 'intra_oral_radiography',
            'PX': 'panoramic_x_ray',
            'GM': 'general_microscopy',
            'SM': 'slide_microscopy',
            'OT': 'other',
            'PT': 'positron_emission_tomography',
            'ES': 'endoscopy',
            'OP': 'ophthalmic_photography',
            'OPM': 'ophthalmic_mapping',
            'OPT': 'ophthalmic_tomography',
            'IVOCT': 'intravascular_optical_coherence_tomography',
            'IVUS': 'intravascular_ultrasound'
        }

        # Medical image file extensions that might contain DICOM data
        self.medical_extensions = {'.dcm', '.dicom', '.ima', '.img'}

        logger.info(f"MedicalImageClassifier initialized - DICOM: {self.dicom_available}, "
                   f"SimpleITK: {self.simpleitk_available}, MedMNIST: {self.medmnist_available}")

    def _check_dicom_availability(self) -> bool:
        """Check if pydicom is available."""
        try:
            import pydicom
            return True
        except ImportError:
            logger.warning("pydicom not available - DICOM analysis will be limited")
            return False

    def _check_simpleitk_availability(self) -> bool:
        """Check if SimpleITK is available."""
        try:
            import SimpleITK as sitk
            return True
        except ImportError:
            logger.warning("SimpleITK not available - advanced medical image analysis will be limited")
            return False

    def _check_medmnist_availability(self) -> bool:
        """Check if MedMNIST is available."""
        try:
            import medmnist
            return True
        except ImportError:
            logger.warning("MedMNIST not available - medical image classification models will be limited")
            return False

    def analyze_medical_image(self, file_bytes: bytes, file_name: str) -> Dict[str, Any]:
        """
        Analyze medical image using DICOM metadata and medical AI models.

        Args:
            file_bytes: Raw image file bytes
            file_name: Name of the image file

        Returns:
            Dictionary containing comprehensive medical image analysis
        """
        try:
            # First, try DICOM analysis if the file might be DICOM
            if self._might_be_dicom(file_bytes, file_name):
                dicom_result = self._analyze_dicom_image(file_bytes, file_name)
                if dicom_result.get('is_dicom', False):
                    return dicom_result

            # Fall back to standard image analysis with medical context
            return self._analyze_standard_medical_image(file_bytes, file_name)

        except Exception as e:
            logger.error(f"Error analyzing medical image {file_name}: {e}")
            return self._create_fallback_analysis(file_bytes, file_name, str(e))

    def _might_be_dicom(self, file_bytes: bytes, file_name: str) -> bool:
        """Check if file might be a DICOM file."""
        # Check file extension
        file_ext = os.path.splitext(file_name)[1].lower()
        if file_ext in self.medical_extensions:
            return True

        # Check DICOM magic bytes
        if len(file_bytes) > 132:
            # DICOM files have "DICM" at offset 128
            return file_bytes[128:132] == b'DICM'

        return False

    def _analyze_dicom_image(self, file_bytes: bytes, file_name: str) -> Dict[str, Any]:
        """Analyze DICOM image and extract medical metadata."""
        if not self.dicom_available:
            return self._analyze_standard_medical_image(file_bytes, file_name)

        try:
            import pydicom

            # Read DICOM file
            dicom_data = pydicom.dcmread(io.BytesIO(file_bytes), force=True)

            # Extract DICOM metadata
            modality = getattr(dicom_data, 'Modality', 'Unknown')
            body_part = getattr(dicom_data, 'BodyPartExamined', 'Unknown')
            study_description = getattr(dicom_data, 'StudyDescription', '')
            series_description = getattr(dicom_data, 'SeriesDescription', '')
            image_type = getattr(dicom_data, 'ImageType', [])
            photometric_interpretation = getattr(dicom_data, 'PhotometricInterpretation', 'Unknown')

            # Get image dimensions
            rows = getattr(dicom_data, 'Rows', 0)
            columns = getattr(dicom_data, 'Columns', 0)

            # Determine medical image type from DICOM modality
            medical_type = self.dicom_modalities.get(modality, 'medical_image')

            # Create comprehensive analysis
            analysis = {
                'is_dicom': True,
                'medical_type': medical_type,
                'modality': modality,
                'body_part_examined': body_part,
                'study_description': study_description,
                'series_description': series_description,
                'image_type': list(image_type) if image_type else [],
                'photometric_interpretation': photometric_interpretation,
                'width': columns,
                'height': rows,
                'file_size_bytes': len(file_bytes),
                'dicom_metadata': {
                    'patient_id': getattr(dicom_data, 'PatientID', ''),
                    'study_date': getattr(dicom_data, 'StudyDate', ''),
                    'acquisition_date': getattr(dicom_data, 'AcquisitionDate', ''),
                    'institution_name': getattr(dicom_data, 'InstitutionName', ''),
                    'manufacturer': getattr(dicom_data, 'Manufacturer', ''),
                    'manufacturer_model': getattr(dicom_data, 'ManufacturerModelName', ''),
                }
            }

            logger.info(f"Successfully analyzed DICOM image: {file_name} - Modality: {modality}")
            return analysis

        except Exception as e:
            logger.warning(f"Failed to analyze as DICOM: {e}")
            return self._analyze_standard_medical_image(file_bytes, file_name)

    def _detect_grayscale_image(self, image: Image.Image) -> bool:
        """
        Enhanced grayscale detection that works regardless of file format or color mode.

        This fixes the validation issue where grayscale X-rays were incorrectly
        identified as color images.
        """
        try:
            # Convert to numpy array for analysis
            img_array = np.array(image)

            # Handle different image modes
            if image.mode in ['L', 'LA', '1']:
                # Already in grayscale mode
                return True
            elif image.mode in ['RGB', 'RGBA']:
                # Check if RGB channels are identical (indicating grayscale content)
                if len(img_array.shape) == 3 and img_array.shape[2] >= 3:
                    r_channel = img_array[:, :, 0]
                    g_channel = img_array[:, :, 1]
                    b_channel = img_array[:, :, 2]

                    # Calculate channel differences
                    rg_diff = np.mean(np.abs(r_channel.astype(float) - g_channel.astype(float)))
                    rb_diff = np.mean(np.abs(r_channel.astype(float) - b_channel.astype(float)))
                    gb_diff = np.mean(np.abs(g_channel.astype(float) - b_channel.astype(float)))

                    # If all channels are very similar, it's effectively grayscale
                    # Threshold of 2.0 allows for minor compression artifacts
                    max_channel_diff = max(rg_diff, rb_diff, gb_diff)
                    is_grayscale = max_channel_diff < 2.0

                    logger.debug(f"Grayscale detection: max_channel_diff={max_channel_diff:.2f}, is_grayscale={is_grayscale}")
                    return is_grayscale
                else:
                    return False
            else:
                # For other modes, assume not grayscale
                return False

        except Exception as e:
            logger.warning(f"Error in grayscale detection: {e}")
            # Fallback to simple mode check
            return image.mode in ['L', 'LA', '1']

    def _analyze_standard_medical_image(self, file_bytes: bytes, file_name: str) -> Dict[str, Any]:
        """Analyze standard medical image using enhanced heuristics and AI models."""
        try:
            # Basic image analysis using PIL
            image = Image.open(io.BytesIO(file_bytes))
            width, height = image.size
            mode = image.mode
            format_type = image.format or "Unknown"

            # Enhanced grayscale detection (fixes the validation issue)
            is_grayscale = self._detect_grayscale_image(image)

            # Enhanced medical image classification
            medical_type = self._classify_medical_image_type(image, file_name)

            # Extract additional medical context
            medical_context = self._extract_medical_context(image, file_name, medical_type)

            # Analyze pathological indicators for condition-aware keyword generation
            img_array = np.array(image)
            pathological_analysis = self._analyze_pathological_indicators(
                img_array, medical_type, medical_context.get('image_characteristics', {})
            )

            # Add pathological analysis to medical context
            medical_context['pathological_analysis'] = pathological_analysis

            analysis = {
                'is_dicom': False,
                'medical_type': medical_type,
                'width': int(width),
                'height': int(height),
                'mode': mode,
                'format': format_type,
                'is_grayscale': bool(is_grayscale),  # Convert numpy bool to Python bool
                'aspect_ratio': round(width / height, 2),
                'file_size_bytes': len(file_bytes),
                'medical_context': self._convert_numpy_types(medical_context)  # Convert all numpy types
            }

            logger.info(f"Successfully analyzed standard medical image: {file_name} - Type: {medical_type}")
            return analysis

        except Exception as e:
            logger.error(f"Failed to analyze standard medical image: {e}")
            return self._create_fallback_analysis(file_bytes, file_name, str(e))

    def _convert_numpy_types(self, obj):
        """
        Recursively convert numpy types to Python native types for JSON serialization.

        Args:
            obj: Object that may contain numpy types

        Returns:
            Object with numpy types converted to Python native types
        """
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {key: self._convert_numpy_types(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_numpy_types(item) for item in obj]
        elif isinstance(obj, tuple):
            return tuple(self._convert_numpy_types(item) for item in obj)
        else:
            return obj

    def _classify_medical_image_type(self, image: Image.Image, file_name: str) -> str:
        """
        Classify medical image type using enhanced heuristics and AI models.

        Args:
            image: PIL Image object
            file_name: Name of the image file

        Returns:
            Medical image type classification
        """
        try:
            # Use MedMNIST models if available
            if self.medmnist_available:
                medmnist_result = self._classify_with_medmnist(image)
                if medmnist_result:
                    return medmnist_result

            # Enhanced heuristic classification
            return self._classify_with_enhanced_heuristics(image, file_name)

        except Exception as e:
            logger.warning(f"Error in medical image classification: {e}")
            return self._classify_with_enhanced_heuristics(image, file_name)

    def _classify_with_medmnist(self, image: Image.Image) -> Optional[str]:
        """Classify medical image using MedMNIST models."""
        try:
            import medmnist
            import torch
            import torchvision.transforms as transforms

            # Convert image to tensor for MedMNIST
            transform = transforms.Compose([
                transforms.Resize((28, 28)),  # MedMNIST standard size
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.5], std=[0.5])
            ])

            # Convert to grayscale if needed
            if image.mode != 'L':
                image = image.convert('L')

            # This is a placeholder for MedMNIST classification
            # In practice, you would load a pre-trained MedMNIST model
            # and use it for classification
            logger.info("MedMNIST classification attempted (placeholder)")
            return None

        except Exception as e:
            logger.warning(f"MedMNIST classification failed: {e}")
            return None

    def _classify_with_enhanced_heuristics(self, image: Image.Image, file_name: str) -> str:
        """
        Patient-centric enhanced heuristic classification for medical images.

        Designed for patients uploading their own medical images with generic filenames
        like "IMG_001.jpg" from phones or scanners.
        """
        width, height = image.size
        is_grayscale = self._detect_grayscale_image(image)
        aspect_ratio = width / height

        # Convert to numpy array for advanced analysis
        img_array = np.array(image)

        # File name analysis (still useful when available)
        file_name_lower = file_name.lower()
        filename_medical_type = self._classify_by_filename(file_name_lower)
        if filename_medical_type:
            return filename_medical_type

        # Patient-centric image content analysis
        # This is the core improvement for handling generic filenames
        content_based_type = self._classify_by_image_content(image, img_array, is_grayscale, aspect_ratio)

        return content_based_type

    def _classify_by_filename(self, file_name_lower: str) -> Optional[str]:
        """Extract medical type from filename if medical terms are present."""
        # Radiological terms
        if any(term in file_name_lower for term in ['xray', 'x-ray', 'chest', 'cxr']):
            return 'chest_xray'
        elif any(term in file_name_lower for term in ['ct', 'computed_tomography']):
            return 'computed_tomography'
        elif any(term in file_name_lower for term in ['mri', 'magnetic_resonance']):
            return 'magnetic_resonance'
        elif any(term in file_name_lower for term in ['ultrasound', 'us', 'echo']):
            return 'ultrasound'
        elif any(term in file_name_lower for term in ['mammo', 'mammography']):
            return 'mammography'

        # Clinical specialties
        elif any(term in file_name_lower for term in ['dermato', 'skin', 'dermatology', 'rash', 'lesion']):
            return 'dermatological_image'
        elif any(term in file_name_lower for term in ['retina', 'fundus', 'ophthalmology', 'eye']):
            return 'retinal_image'
        elif any(term in file_name_lower for term in ['pathology', 'histology', 'microscopy', 'biopsy']):
            return 'pathological_image'
        elif any(term in file_name_lower for term in ['endoscopy', 'endoscopic', 'colonoscopy']):
            return 'endoscopy'

        # Lab and document terms
        elif any(term in file_name_lower for term in ['lab', 'blood', 'test', 'result']):
            return 'lab_result_document'
        elif any(term in file_name_lower for term in ['report', 'discharge', 'summary']):
            return 'medical_document'

        return None

    def _classify_by_image_content(self, image: Image.Image, img_array: np.ndarray,
                                 is_grayscale: bool, aspect_ratio: float) -> str:
        """
        Classify medical images based on content analysis - the core patient-centric improvement.

        This method analyzes image characteristics to determine medical image type
        without relying on filenames or directory structure.
        """
        width, height = image.size

        # Analyze image characteristics for medical classification
        image_characteristics = self._analyze_detailed_image_characteristics(img_array, is_grayscale)

        # Classification logic based on medical image patterns
        if is_grayscale:
            return self._classify_grayscale_medical_image(
                width, height, aspect_ratio, image_characteristics
            )
        else:
            return self._classify_color_medical_image(
                width, height, aspect_ratio, image_characteristics, img_array
            )

    def _analyze_detailed_image_characteristics(self, img_array: np.ndarray, is_grayscale: bool) -> Dict[str, Any]:
        """Analyze detailed image characteristics for medical classification."""
        try:
            characteristics = {}

            # Basic intensity statistics
            if is_grayscale or len(img_array.shape) == 2:
                # Grayscale analysis
                flat_array = img_array.flatten() if len(img_array.shape) == 2 else img_array[:,:,0].flatten()
                characteristics.update({
                    'mean_intensity': float(np.mean(flat_array)),
                    'std_intensity': float(np.std(flat_array)),
                    'min_intensity': float(np.min(flat_array)),
                    'max_intensity': float(np.max(flat_array)),
                    'intensity_range': float(np.max(flat_array) - np.min(flat_array)),
                    'contrast_ratio': float(np.std(flat_array) / np.mean(flat_array)) if np.mean(flat_array) > 0 else 0
                })

                # Medical imaging specific characteristics
                characteristics.update({
                    'has_high_contrast': characteristics['contrast_ratio'] > 0.5,
                    'has_dark_background': characteristics['mean_intensity'] < 100,
                    'has_bright_regions': characteristics['max_intensity'] > 200,
                    'intensity_distribution': self._analyze_intensity_distribution(flat_array)
                })
            else:
                # Color analysis
                characteristics.update({
                    'mean_rgb': [float(np.mean(img_array[:,:,i])) for i in range(min(3, img_array.shape[2]))],
                    'color_variance': float(np.var(img_array)),
                    'dominant_color_channel': int(np.argmax([np.mean(img_array[:,:,i]) for i in range(min(3, img_array.shape[2]))])),
                    'skin_tone_likelihood': self._analyze_skin_tone_likelihood(img_array)
                })

            # Texture and pattern analysis
            characteristics.update({
                'edge_density': self._calculate_edge_density(img_array),
                'texture_complexity': self._calculate_texture_complexity(img_array),
                'has_regular_patterns': self._detect_regular_patterns(img_array)
            })

            return characteristics

        except Exception as e:
            logger.warning(f"Error in detailed image analysis: {e}")
            return {}

    def _analyze_intensity_distribution(self, flat_array: np.ndarray) -> Dict[str, float]:
        """Analyze intensity distribution patterns typical in medical images."""
        try:
            hist, _ = np.histogram(flat_array, bins=50, range=(0, 255))
            hist_normalized = hist / np.sum(hist)

            # Find peaks in histogram
            peak_indices = []
            for i in range(1, len(hist_normalized) - 1):
                if hist_normalized[i] > hist_normalized[i-1] and hist_normalized[i] > hist_normalized[i+1]:
                    if hist_normalized[i] > 0.02:  # Significant peak
                        peak_indices.append(i)

            return {
                'num_peaks': len(peak_indices),
                'has_bimodal_distribution': len(peak_indices) == 2,
                'background_peak_ratio': float(hist_normalized[0]) if len(hist_normalized) > 0 else 0,
                'intensity_skewness': float(np.mean(flat_array) - np.median(flat_array))
            }
        except:
            return {'num_peaks': 0, 'has_bimodal_distribution': False, 'background_peak_ratio': 0, 'intensity_skewness': 0}

    def _analyze_skin_tone_likelihood(self, img_array: np.ndarray) -> float:
        """Analyze likelihood that image contains skin tones (for dermatology classification)."""
        try:
            if len(img_array.shape) != 3 or img_array.shape[2] < 3:
                return 0.0

            # Define skin tone ranges in RGB
            # These are broad ranges to capture diverse skin tones
            skin_ranges = [
                # Light skin tones
                {'r': (180, 255), 'g': (120, 220), 'b': (100, 200)},
                # Medium skin tones
                {'r': (120, 200), 'g': (80, 160), 'b': (60, 140)},
                # Dark skin tones
                {'r': (60, 140), 'g': (40, 100), 'b': (30, 80)}
            ]

            total_pixels = img_array.shape[0] * img_array.shape[1]
            skin_pixels = 0

            for skin_range in skin_ranges:
                mask = (
                    (img_array[:,:,0] >= skin_range['r'][0]) & (img_array[:,:,0] <= skin_range['r'][1]) &
                    (img_array[:,:,1] >= skin_range['g'][0]) & (img_array[:,:,1] <= skin_range['g'][1]) &
                    (img_array[:,:,2] >= skin_range['b'][0]) & (img_array[:,:,2] <= skin_range['b'][1])
                )
                skin_pixels += np.sum(mask)

            skin_ratio = skin_pixels / total_pixels
            return min(1.0, skin_ratio * 2)  # Amplify the ratio but cap at 1.0

        except Exception as e:
            logger.warning(f"Error in skin tone analysis: {e}")
            return 0.0

    def _calculate_edge_density(self, img_array: np.ndarray) -> float:
        """Calculate edge density to help identify medical image types."""
        try:
            # Convert to grayscale if needed
            if len(img_array.shape) == 3:
                gray = np.mean(img_array, axis=2)
            else:
                gray = img_array

            # Simple edge detection using gradient
            grad_x = np.abs(np.diff(gray, axis=1))
            grad_y = np.abs(np.diff(gray, axis=0))

            # Calculate edge density
            edge_threshold = np.std(gray) * 0.5
            edges_x = np.sum(grad_x > edge_threshold)
            edges_y = np.sum(grad_y > edge_threshold)

            total_possible_edges = gray.shape[0] * (gray.shape[1] - 1) + (gray.shape[0] - 1) * gray.shape[1]
            edge_density = (edges_x + edges_y) / total_possible_edges

            return float(edge_density)

        except Exception as e:
            logger.warning(f"Error calculating edge density: {e}")
            return 0.0

    def _calculate_texture_complexity(self, img_array: np.ndarray) -> float:
        """Calculate texture complexity to distinguish medical image types."""
        try:
            # Convert to grayscale if needed
            if len(img_array.shape) == 3:
                gray = np.mean(img_array, axis=2)
            else:
                gray = img_array

            # Calculate local variance as a measure of texture
            # Use a 5x5 window
            kernel_size = 5
            pad_size = kernel_size // 2

            # Pad the image
            padded = np.pad(gray, pad_size, mode='reflect')

            # Calculate local variance
            local_vars = []
            for i in range(gray.shape[0]):
                for j in range(gray.shape[1]):
                    window = padded[i:i+kernel_size, j:j+kernel_size]
                    local_vars.append(np.var(window))

            # Texture complexity is the variance of local variances
            texture_complexity = np.var(local_vars) / (np.mean(local_vars) + 1e-6)

            return float(texture_complexity)

        except Exception as e:
            logger.warning(f"Error calculating texture complexity: {e}")
            return 0.0

    def _detect_regular_patterns(self, img_array: np.ndarray) -> bool:
        """Detect regular patterns that might indicate specific medical image types."""
        try:
            # Convert to grayscale if needed
            if len(img_array.shape) == 3:
                gray = np.mean(img_array, axis=2)
            else:
                gray = img_array

            # Look for regular patterns using autocorrelation
            # Sample a smaller region for efficiency
            sample_size = min(256, min(gray.shape))
            center_x, center_y = gray.shape[0] // 2, gray.shape[1] // 2
            start_x = max(0, center_x - sample_size // 2)
            start_y = max(0, center_y - sample_size // 2)
            sample = gray[start_x:start_x+sample_size, start_y:start_y+sample_size]

            # Simple pattern detection using row/column variance
            row_means = np.mean(sample, axis=1)
            col_means = np.mean(sample, axis=0)

            row_regularity = np.std(row_means) / (np.mean(row_means) + 1e-6)
            col_regularity = np.std(col_means) / (np.mean(col_means) + 1e-6)

            # If both row and column patterns are very regular, it might be a grid/pattern
            has_patterns = row_regularity < 0.1 or col_regularity < 0.1

            return bool(has_patterns)

        except Exception as e:
            logger.warning(f"Error detecting regular patterns: {e}")
            return False

    def _classify_grayscale_medical_image(self, width: int, height: int, aspect_ratio: float,
                                        characteristics: Dict[str, Any]) -> str:
        """
        Classify grayscale medical images based on content analysis.

        This is crucial for patient-uploaded images where filenames don't help.
        """
        # Extract key characteristics
        has_high_contrast = characteristics.get('has_high_contrast', False)
        has_dark_background = characteristics.get('has_dark_background', False)
        has_bright_regions = characteristics.get('has_bright_regions', False)
        edge_density = characteristics.get('edge_density', 0)
        texture_complexity = characteristics.get('texture_complexity', 0)
        intensity_dist = characteristics.get('intensity_distribution', {})

        # High resolution, high contrast, dark background -> likely X-ray
        if (width > 1000 or height > 1000) and has_high_contrast and has_dark_background:
            if aspect_ratio > 1.1:  # Landscape orientation
                return 'chest_xray'
            elif 0.8 <= aspect_ratio <= 1.2:  # Square-ish
                return 'radiological_scan'  # Could be CT, MRI
            else:  # Portrait
                return 'medical_radiograph'

        # Medium to high resolution with bimodal intensity distribution -> CT/MRI
        elif (width >= 512 and height >= 512) and intensity_dist.get('has_bimodal_distribution', False):
            if 0.8 <= aspect_ratio <= 1.2:  # Square typical of CT/MRI
                if edge_density > 0.1:  # High edge density suggests CT
                    return 'computed_tomography'
                else:  # Lower edge density suggests MRI
                    return 'magnetic_resonance'
            else:
                return 'radiological_scan'

        # High texture complexity might indicate ultrasound
        elif texture_complexity > 1.0 and not has_high_contrast:
            return 'ultrasound'

        # Lower resolution grayscale images
        elif width < 512 or height < 512:
            if has_high_contrast:
                return 'medical_radiograph'
            else:
                return 'clinical_photograph'  # Might be grayscale clinical photo

        # Default for grayscale medical images
        else:
            return 'medical_radiograph'

    def _classify_color_medical_image(self, width: int, height: int, aspect_ratio: float,
                                    characteristics: Dict[str, Any], img_array: np.ndarray) -> str:
        """
        Classify color medical images based on content analysis.

        Critical for dermatology, ophthalmology, and clinical photography.
        """
        # Extract key characteristics
        skin_tone_likelihood = characteristics.get('skin_tone_likelihood', 0)
        edge_density = characteristics.get('edge_density', 0)
        texture_complexity = characteristics.get('texture_complexity', 0)
        color_variance = characteristics.get('color_variance', 0)
        mean_rgb = characteristics.get('mean_rgb', [0, 0, 0])

        # High skin tone likelihood -> dermatological image
        if skin_tone_likelihood > 0.3:
            # Additional checks for dermatology
            if self._has_dermatological_characteristics(img_array, characteristics):
                return 'dermatological_image'
            else:
                return 'clinical_photograph'

        # Check for ophthalmological characteristics
        elif self._has_ophthalmological_characteristics(img_array, characteristics):
            return 'retinal_image'

        # Check for pathological/microscopy characteristics
        elif self._has_pathological_characteristics(img_array, characteristics):
            return 'pathological_image'

        # Check for endoscopic characteristics
        elif self._has_endoscopic_characteristics(img_array, characteristics):
            return 'endoscopy'

        # High resolution clinical images
        elif width > 1500 or height > 1500:
            return 'high_resolution_clinical_image'

        # Document-like characteristics (lab results, reports)
        elif self._has_document_characteristics(img_array, characteristics):
            return 'medical_document'

        # Default for color medical images
        else:
            return 'clinical_photograph'

    def _has_dermatological_characteristics(self, img_array: np.ndarray, characteristics: Dict[str, Any]) -> bool:
        """Detect characteristics specific to dermatological images."""
        try:
            skin_tone_likelihood = characteristics.get('skin_tone_likelihood', 0)
            edge_density = characteristics.get('edge_density', 0)
            texture_complexity = characteristics.get('texture_complexity', 0)

            # Strong indicators for dermatology
            if skin_tone_likelihood > 0.5:  # High skin content
                return True

            # Medium skin content with specific texture patterns
            if skin_tone_likelihood > 0.2 and texture_complexity > 0.5:
                return True

            # Check for lesion-like characteristics (darker regions on skin background)
            if len(img_array.shape) == 3 and skin_tone_likelihood > 0.1:
                # Look for darker regions that might be lesions
                gray = np.mean(img_array, axis=2)
                mean_intensity = np.mean(gray)
                dark_regions = np.sum(gray < mean_intensity * 0.7) / gray.size

                if dark_regions > 0.05:  # At least 5% darker regions
                    return True

            return False

        except Exception as e:
            logger.warning(f"Error in dermatological analysis: {e}")
            return False

    def _analyze_pathological_indicators(self, img_array: np.ndarray, medical_type: str,
                                       characteristics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze image for pathological indicators vs. normal findings.

        This is crucial for generating appropriate medical keywords and descriptions
        that don't unnecessarily alarm patients with pathological terms for normal images.
        """
        try:
            pathological_analysis = {
                'has_pathological_findings': False,
                'pathological_confidence': 0.0,
                'specific_findings': [],
                'normal_indicators': [],
                'clinical_significance': 'routine_documentation'
            }

            if medical_type == 'dermatological_image':
                pathological_analysis.update(self._analyze_dermatological_pathology(img_array, characteristics))
            elif medical_type in ['chest_xray', 'computed_tomography', 'magnetic_resonance', 'radiological_scan']:
                pathological_analysis.update(self._analyze_radiological_pathology(img_array, characteristics))
            elif medical_type == 'clinical_photograph':
                pathological_analysis.update(self._analyze_clinical_photo_pathology(img_array, characteristics))
            elif medical_type == 'pathological_image':
                pathological_analysis.update(self._analyze_histological_pathology(img_array, characteristics))

            return pathological_analysis

        except Exception as e:
            logger.warning(f"Error in pathological analysis: {e}")
            return {
                'has_pathological_findings': False,
                'pathological_confidence': 0.0,
                'specific_findings': [],
                'normal_indicators': ['analysis_limited'],
                'clinical_significance': 'routine_documentation'
            }

    def _analyze_dermatological_pathology(self, img_array: np.ndarray, characteristics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze dermatological images for pathological vs. normal skin findings.

        Enhanced version with improved clinical sensitivity for subtle skin conditions
        like rosacea, hypopigmentation, and skin irritation.
        """
        try:
            findings = {
                'has_pathological_findings': False,
                'pathological_confidence': 0.0,
                'specific_findings': [],
                'normal_indicators': [],
                'clinical_significance': 'skin_documentation'
            }

            # Get image characteristics
            skin_tone_likelihood = characteristics.get('skin_tone_likelihood', 0)
            edge_density = characteristics.get('edge_density', 0)
            texture_complexity = characteristics.get('texture_complexity', 0)

            if len(img_array.shape) != 3:
                return findings

            # Convert to grayscale for analysis
            gray = np.mean(img_array, axis=2)
            mean_intensity = np.mean(gray)
            std_intensity = np.std(gray)

            pathological_score = 0.0

            # Enhanced analysis for subtle skin conditions

            # 1. Analyze color uniformity with improved sensitivity
            color_variance = np.var(img_array)
            # Lowered threshold for better detection of subtle conditions
            if color_variance > 1500:  # Reduced from 2000 for better sensitivity
                pathological_score += 0.25  # Increased weight
                findings['specific_findings'].append('color_variation')
            elif color_variance < 800:  # More specific threshold for normal
                findings['normal_indicators'].append('uniform_coloration')

            # 2. Enhanced redness detection for rosacea and irritation
            redness_score = self._analyze_redness_patterns(img_array)
            if redness_score > 0.3:  # New threshold for redness detection
                pathological_score += 0.3
                findings['specific_findings'].append('redness_pattern')
            elif redness_score < 0.1:
                findings['normal_indicators'].append('normal_coloration')

            # 3. Improved intensity distribution analysis for subtle lesions
            # More sensitive thresholds for detecting hypopigmentation and hyperpigmentation
            very_dark_regions = np.sum(gray < mean_intensity - 1.5 * std_intensity) / gray.size  # Reduced from 2*
            very_bright_regions = np.sum(gray > mean_intensity + 1.5 * std_intensity) / gray.size  # Reduced from 2*

            if very_dark_regions > 0.05:  # Reduced from 0.1 for better sensitivity
                pathological_score += 0.25  # Reduced weight to balance
                findings['specific_findings'].append('hyperpigmentation_areas')
            elif very_dark_regions < 0.01:
                findings['normal_indicators'].append('consistent_pigmentation')

            if very_bright_regions > 0.05:  # Reduced from 0.1 for better sensitivity
                pathological_score += 0.25  # Reduced weight
                findings['specific_findings'].append('hypopigmentation_areas')

            # 4. Enhanced edge density analysis for subtle lesion borders
            if edge_density > 0.12:  # Reduced from 0.15 for better sensitivity
                pathological_score += 0.2
                findings['specific_findings'].append('defined_borders')
            elif edge_density < 0.08:  # More specific threshold
                findings['normal_indicators'].append('smooth_texture')

            # 5. Enhanced texture analysis for skin conditions
            if texture_complexity > 1.2:  # Reduced from 1.5 for better sensitivity
                pathological_score += 0.2
                findings['specific_findings'].append('texture_irregularity')
            elif texture_complexity < 0.8:  # More specific threshold
                findings['normal_indicators'].append('normal_texture')

            # 6. Enhanced lesion detection with improved sensitivity
            lesion_shapes = self._detect_potential_lesions(gray)
            if lesion_shapes > 0:
                pathological_score += 0.25  # Reduced from 0.3 to balance
                findings['specific_findings'].append('potential_lesions')
            else:
                findings['normal_indicators'].append('no_obvious_lesions')

            # 7. New: Analyze skin tone variations for subtle conditions
            tone_variation_score = self._analyze_skin_tone_variations(img_array)
            if tone_variation_score > 0.4:
                pathological_score += 0.2
                findings['specific_findings'].append('skin_tone_variation')

            # Determine overall assessment with improved thresholds
            findings['pathological_confidence'] = min(1.0, pathological_score)

            # Lowered thresholds for better clinical sensitivity
            if pathological_score > 0.4:  # Reduced from 0.5
                findings['has_pathological_findings'] = True
                findings['clinical_significance'] = 'condition_monitoring'
            elif pathological_score > 0.25:  # Reduced from 0.3
                findings['has_pathological_findings'] = True
                findings['clinical_significance'] = 'follow_up_recommended'
            else:
                findings['clinical_significance'] = 'routine_skin_documentation'

            return findings

        except Exception as e:
            logger.warning(f"Error in dermatological pathology analysis: {e}")
            return {
                'has_pathological_findings': False,
                'pathological_confidence': 0.0,
                'specific_findings': [],
                'normal_indicators': ['analysis_limited'],
                'clinical_significance': 'routine_documentation'
            }

    def _analyze_redness_patterns(self, img_array: np.ndarray) -> float:
        """
        Analyze redness patterns in skin images for detecting rosacea and irritation.

        Returns:
            Float score between 0-1 indicating redness intensity
        """
        try:
            if len(img_array.shape) != 3:
                return 0.0

            # Extract RGB channels
            r_channel = img_array[:, :, 0].astype(float)
            g_channel = img_array[:, :, 1].astype(float)
            b_channel = img_array[:, :, 2].astype(float)

            # Calculate redness ratio (R relative to G and B)
            # Avoid division by zero
            denominator = g_channel + b_channel + 1
            redness_ratio = r_channel / denominator

            # Calculate mean redness across the image
            mean_redness = np.mean(redness_ratio)

            # Look for areas with significantly higher redness
            redness_threshold = mean_redness + np.std(redness_ratio)
            high_redness_areas = np.sum(redness_ratio > redness_threshold) / redness_ratio.size

            # Combine mean redness and high redness area percentage
            redness_score = (mean_redness * 0.7) + (high_redness_areas * 0.3)

            return min(1.0, redness_score)

        except Exception as e:
            logger.warning(f"Error in redness pattern analysis: {e}")
            return 0.0

    def _analyze_skin_tone_variations(self, img_array: np.ndarray) -> float:
        """
        Analyze skin tone variations for detecting subtle pigmentation changes.

        Returns:
            Float score between 0-1 indicating tone variation intensity
        """
        try:
            if len(img_array.shape) != 3:
                return 0.0

            # Convert to LAB color space for better skin tone analysis
            # Approximate LAB conversion for basic analysis
            r, g, b = img_array[:, :, 0], img_array[:, :, 1], img_array[:, :, 2]

            # Calculate luminance (L channel approximation)
            luminance = 0.299 * r + 0.587 * g + 0.114 * b

            # Calculate local variations in luminance
            # Use a simple gradient approach
            grad_x = np.abs(np.diff(luminance, axis=1))
            grad_y = np.abs(np.diff(luminance, axis=0))

            # Calculate variation metrics
            mean_grad_x = np.mean(grad_x) if grad_x.size > 0 else 0
            mean_grad_y = np.mean(grad_y) if grad_y.size > 0 else 0

            # Combine gradients for overall variation score
            variation_score = (mean_grad_x + mean_grad_y) / 255.0  # Normalize to 0-1

            return min(1.0, variation_score * 2)  # Amplify but cap at 1.0

        except Exception as e:
            logger.warning(f"Error in skin tone variation analysis: {e}")
            return 0.0

    def _detect_potential_lesions(self, gray_image: np.ndarray) -> int:
        """Detect potential lesion-like shapes in grayscale image."""
        try:
            # Simple lesion detection using intensity thresholding
            mean_intensity = np.mean(gray_image)
            std_intensity = np.std(gray_image)

            # Look for regions significantly darker than average
            threshold = mean_intensity - 1.5 * std_intensity
            dark_regions = gray_image < threshold

            # Count connected components (potential lesions)
            # This is a simplified approach - in production, you might use more sophisticated methods
            from scipy import ndimage
            labeled_array, num_features = ndimage.label(dark_regions)

            # Filter out very small or very large regions
            lesion_count = 0
            for i in range(1, num_features + 1):
                region_size = np.sum(labeled_array == i)
                total_pixels = gray_image.size
                region_ratio = region_size / total_pixels

                # Consider regions between 0.1% and 20% of image as potential lesions
                if 0.001 < region_ratio < 0.2:
                    lesion_count += 1

            return lesion_count

        except Exception as e:
            logger.warning(f"Error in lesion detection: {e}")
            return 0

    def _analyze_radiological_pathology(self, img_array: np.ndarray, characteristics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze radiological images for pathological vs. normal findings."""
        try:
            findings = {
                'has_pathological_findings': False,
                'pathological_confidence': 0.0,
                'specific_findings': [],
                'normal_indicators': ['routine_imaging'],
                'clinical_significance': 'screening_examination'
            }

            # For radiological images, we're more conservative about pathological findings
            # Most patient-uploaded X-rays are for documentation, not active diagnosis
            edge_density = characteristics.get('edge_density', 0)
            texture_complexity = characteristics.get('texture_complexity', 0)

            # Only flag as pathological if there are very obvious abnormalities
            if edge_density > 0.2 and texture_complexity > 2.0:
                findings['pathological_confidence'] = 0.3
                findings['specific_findings'].append('image_complexity')
                findings['clinical_significance'] = 'professional_review_recommended'

            return findings

        except Exception as e:
            logger.warning(f"Error in radiological pathology analysis: {e}")
            return {
                'has_pathological_findings': False,
                'pathological_confidence': 0.0,
                'specific_findings': [],
                'normal_indicators': ['routine_imaging'],
                'clinical_significance': 'screening_examination'
            }

    def _analyze_clinical_photo_pathology(self, img_array: np.ndarray, characteristics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze clinical photographs for pathological vs. normal findings."""
        try:
            findings = {
                'has_pathological_findings': False,
                'pathological_confidence': 0.0,
                'specific_findings': [],
                'normal_indicators': ['clinical_documentation'],
                'clinical_significance': 'routine_documentation'
            }

            # Clinical photos are often documentation, be conservative
            color_variance = characteristics.get('color_variance', 0)
            edge_density = characteristics.get('edge_density', 0)

            if color_variance > 3000 and edge_density > 0.15:
                findings['pathological_confidence'] = 0.2
                findings['specific_findings'].append('visual_variation')
                findings['clinical_significance'] = 'clinical_correlation_recommended'

            return findings

        except Exception as e:
            logger.warning(f"Error in clinical photo pathology analysis: {e}")
            return findings

    def _analyze_histological_pathology(self, img_array: np.ndarray, characteristics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze histological/pathology images for findings."""
        try:
            findings = {
                'has_pathological_findings': True,  # Pathology images are inherently for diagnosis
                'pathological_confidence': 0.8,
                'specific_findings': ['histological_analysis'],
                'normal_indicators': [],
                'clinical_significance': 'pathological_examination'
            }

            return findings

        except Exception as e:
            logger.warning(f"Error in histological pathology analysis: {e}")
            return findings

    def _has_ophthalmological_characteristics(self, img_array: np.ndarray, characteristics: Dict[str, Any]) -> bool:
        """Detect characteristics specific to retinal/eye images."""
        try:
            if len(img_array.shape) != 3:
                return False

            # Look for circular patterns typical of retinal images
            height, width = img_array.shape[:2]
            center_x, center_y = width // 2, height // 2

            # Check if image has a dark circular border (typical of retinal images)
            # Sample points around the edge
            edge_darkness = 0
            edge_samples = 0

            for angle in np.linspace(0, 2*np.pi, 16):
                x = int(center_x + 0.4 * width * np.cos(angle))
                y = int(center_y + 0.4 * height * np.sin(angle))

                if 0 <= x < width and 0 <= y < height:
                    pixel_intensity = np.mean(img_array[y, x])
                    if pixel_intensity < 50:  # Dark border
                        edge_darkness += 1
                    edge_samples += 1

            # If most of the edge is dark, might be retinal image
            if edge_samples > 0 and edge_darkness / edge_samples > 0.6:
                return True

            # Check for reddish coloration typical of retinal images
            mean_rgb = characteristics.get('mean_rgb', [0, 0, 0])
            if len(mean_rgb) >= 3 and mean_rgb[0] > mean_rgb[1] and mean_rgb[0] > mean_rgb[2]:
                # Red channel dominant, check if it's significantly higher
                if mean_rgb[0] > mean_rgb[1] * 1.2 and mean_rgb[0] > mean_rgb[2] * 1.2:
                    return True

            return False

        except Exception as e:
            logger.warning(f"Error in ophthalmological analysis: {e}")
            return False

    def _has_pathological_characteristics(self, img_array: np.ndarray, characteristics: Dict[str, Any]) -> bool:
        """Detect characteristics specific to pathological/microscopy images."""
        try:
            texture_complexity = characteristics.get('texture_complexity', 0)
            color_variance = characteristics.get('color_variance', 0)
            edge_density = characteristics.get('edge_density', 0)

            # High texture complexity and color variance suggest microscopy
            if texture_complexity > 2.0 and color_variance > 1000:
                return True

            # Check for cellular patterns (high edge density with complex textures)
            if edge_density > 0.15 and texture_complexity > 1.5:
                return True

            # Check for typical histology staining colors (pink/purple H&E staining)
            if len(img_array.shape) == 3:
                mean_rgb = characteristics.get('mean_rgb', [0, 0, 0])
                if len(mean_rgb) >= 3:
                    # H&E staining typically has pink (eosin) and purple/blue (hematoxylin)
                    has_pink = mean_rgb[0] > 150 and mean_rgb[1] < mean_rgb[0] * 0.8
                    has_purple = mean_rgb[2] > 120 and mean_rgb[0] < mean_rgb[2] * 0.9

                    if has_pink or has_purple:
                        return True

            return False

        except Exception as e:
            logger.warning(f"Error in pathological analysis: {e}")
            return False

    def _has_endoscopic_characteristics(self, img_array: np.ndarray, characteristics: Dict[str, Any]) -> bool:
        """Detect characteristics specific to endoscopic images."""
        try:
            # Endoscopic images often have dark borders and specific lighting
            if len(img_array.shape) != 3:
                return False

            height, width = img_array.shape[:2]

            # Check for dark corners/borders typical of endoscopic images
            corner_darkness = 0
            corners = [
                (0, 0), (0, width-1), (height-1, 0), (height-1, width-1),
                (height//4, width//4), (height//4, 3*width//4),
                (3*height//4, width//4), (3*height//4, 3*width//4)
            ]

            for y, x in corners:
                if np.mean(img_array[y, x]) < 30:  # Very dark
                    corner_darkness += 1

            # If many corners are dark, might be endoscopic
            if corner_darkness >= 4:
                return True

            # Check for reddish/pinkish coloration typical of internal tissues
            mean_rgb = characteristics.get('mean_rgb', [0, 0, 0])
            if len(mean_rgb) >= 3:
                # Reddish coloration
                if mean_rgb[0] > 100 and mean_rgb[0] > mean_rgb[1] * 1.1:
                    return True

            return False

        except Exception as e:
            logger.warning(f"Error in endoscopic analysis: {e}")
            return False

    def _has_document_characteristics(self, img_array: np.ndarray, characteristics: Dict[str, Any]) -> bool:
        """Detect characteristics of medical documents (lab results, reports)."""
        try:
            edge_density = characteristics.get('edge_density', 0)
            has_regular_patterns = characteristics.get('has_regular_patterns', False)

            # Documents typically have regular patterns (text lines, tables)
            if has_regular_patterns and edge_density > 0.05:
                return True

            # Check for high contrast text-like patterns
            if len(img_array.shape) == 3:
                gray = np.mean(img_array, axis=2)
            else:
                gray = img_array

            # Look for horizontal line patterns (text lines)
            row_means = np.mean(gray, axis=1)
            row_variance = np.var(row_means)

            # High variance in row means suggests text lines
            if row_variance > 100:
                return True

            # Check for predominantly white background with dark text
            mean_intensity = np.mean(gray)
            if mean_intensity > 200:  # Bright background
                dark_pixels = np.sum(gray < 100) / gray.size
                if 0.05 < dark_pixels < 0.3:  # 5-30% dark pixels (text)
                    return True

            return False

        except Exception as e:
            logger.warning(f"Error in document analysis: {e}")
            return False

    def _extract_medical_context(self, image: Image.Image, file_name: str, medical_type: str) -> Dict[str, Any]:
        """Extract additional medical context from image analysis."""
        context = {
            'image_characteristics': self._analyze_image_characteristics(image),
            'filename_indicators': self._extract_filename_indicators(file_name),
            'medical_relevance_score': self._calculate_medical_relevance_score(image, file_name, medical_type)
        }

        return context

    def _analyze_image_characteristics(self, image: Image.Image) -> Dict[str, Any]:
        """Analyze detailed image characteristics relevant to medical imaging."""
        try:
            # Convert to numpy array for analysis
            img_array = np.array(image)

            characteristics = {
                'mean_intensity': float(np.mean(img_array)),
                'std_intensity': float(np.std(img_array)),
                'min_intensity': float(np.min(img_array)),
                'max_intensity': float(np.max(img_array)),
                'dynamic_range': float(np.max(img_array) - np.min(img_array)),
            }

            # Calculate contrast metrics
            if len(img_array.shape) == 2:  # Grayscale
                characteristics['contrast_ratio'] = float(np.std(img_array) / np.mean(img_array)) if np.mean(img_array) > 0 else 0

            return characteristics

        except Exception as e:
            logger.warning(f"Error analyzing image characteristics: {e}")
            return {}

    def _extract_filename_indicators(self, file_name: str) -> List[str]:
        """Extract medical indicators from filename."""
        indicators = []
        file_name_lower = file_name.lower()

        medical_terms = [
            'xray', 'x-ray', 'chest', 'cxr', 'ct', 'mri', 'ultrasound', 'us',
            'mammo', 'mammography', 'endoscopy', 'dermato', 'retina', 'fundus',
            'pathology', 'histology', 'microscopy', 'radiograph', 'scan'
        ]

        for term in medical_terms:
            if term in file_name_lower:
                indicators.append(term)

        return indicators

    def _calculate_medical_relevance_score(self, image: Image.Image, file_name: str, medical_type: str) -> float:
        """Calculate a relevance score for medical context."""
        score = 0.5  # Base score

        # Filename indicators
        filename_indicators = self._extract_filename_indicators(file_name)
        score += len(filename_indicators) * 0.1

        # Image characteristics
        if image.mode in ['L', 'LA', '1']:  # Grayscale often indicates medical imaging
            score += 0.2

        # Size considerations
        width, height = image.size
        if width >= 512 and height >= 512:  # Medical images often high resolution
            score += 0.1

        # Medical type specificity
        if medical_type != 'medical_image':  # More specific than generic
            score += 0.2

        return min(1.0, score)  # Cap at 1.0

    def _create_fallback_analysis(self, file_bytes: bytes, file_name: str, error_msg: str) -> Dict[str, Any]:
        """Create fallback analysis when other methods fail."""
        return {
            'is_dicom': False,
            'medical_type': 'medical_image',
            'file_size_bytes': len(file_bytes),
            'analysis_error': error_msg,
            'fallback_analysis': True,
            'medical_context': {
                'filename_indicators': self._extract_filename_indicators(file_name),
                'medical_relevance_score': 0.3  # Low confidence fallback
            }
        }

    def create_medical_description(self, file_name: str, analysis: Dict[str, Any]) -> str:
        """
        Create comprehensive patient-centric medical image description for embedding.

        Generates descriptions suitable for both patients and healthcare providers,
        optimized for BiomedVLP embedding and medical RAG retrieval.

        Args:
            file_name: Name of the image file
            analysis: Analysis results from analyze_medical_image

        Returns:
            Comprehensive medical description string
        """
        description_parts = []

        # Start with patient-friendly medical type
        medical_type = analysis.get('medical_type', 'medical_image')
        patient_friendly_type = self._get_patient_friendly_type_name(medical_type)
        description_parts.append(f"Medical image: {patient_friendly_type}")

        # Add technical classification for healthcare providers
        if medical_type != patient_friendly_type.lower().replace(' ', '_'):
            description_parts.append(f"Classification: {medical_type.replace('_', ' ')}")

        # Add DICOM-specific information (technical details for providers)
        if analysis.get('is_dicom', False):
            modality = analysis.get('modality', 'Unknown')
            description_parts.append(f"DICOM modality: {modality}")

            body_part = analysis.get('body_part_examined', '')
            if body_part and body_part != 'Unknown':
                description_parts.append(f"Anatomical region: {body_part}")

            study_desc = analysis.get('study_description', '')
            if study_desc:
                description_parts.append(f"Clinical study: {study_desc}")

            series_desc = analysis.get('series_description', '')
            if series_desc:
                description_parts.append(f"Image series: {series_desc}")

        # Add clinical context based on image type
        clinical_context = self._generate_clinical_context(medical_type, analysis)
        if clinical_context:
            description_parts.append(clinical_context)

        # Add image technical details
        if 'width' in analysis and 'height' in analysis:
            resolution = f"{analysis['width']}x{analysis['height']}"
            description_parts.append(f"Resolution: {resolution}")

            # Add quality indicators
            if analysis['width'] >= 1024 or analysis['height'] >= 1024:
                description_parts.append("High resolution imaging")

        # Add imaging characteristics
        if analysis.get('is_grayscale', False):
            description_parts.append("Grayscale medical imaging")
        else:
            description_parts.append("Color clinical imaging")

        # Add content-based medical indicators
        medical_context = analysis.get('medical_context', {})

        # Enhanced medical indicators (beyond just filename)
        all_indicators = self._extract_comprehensive_medical_indicators(analysis, medical_context)
        if all_indicators:
            description_parts.append(f"Medical features: {', '.join(all_indicators)}")

        # Add confidence and quality indicators
        relevance_score = medical_context.get('medical_relevance_score', 0)
        confidence_level = self._get_confidence_description(relevance_score, analysis)
        if confidence_level:
            description_parts.append(confidence_level)

        # Add searchable medical keywords for RAG
        medical_keywords = self._generate_medical_keywords(medical_type, analysis)
        if medical_keywords:
            description_parts.append(f"Medical keywords: {', '.join(medical_keywords)}")

        return ". ".join(description_parts) + "."

    def _get_patient_friendly_type_name(self, medical_type: str) -> str:
        """Convert technical medical type to patient-friendly name."""
        friendly_names = {
            'chest_xray': 'Chest X-ray',
            'computed_tomography': 'CT scan',
            'magnetic_resonance': 'MRI scan',
            'ultrasound': 'Ultrasound image',
            'mammography': 'Mammogram',
            'dermatological_image': 'Skin condition photo',
            'retinal_image': 'Eye examination photo',
            'pathological_image': 'Tissue sample image',
            'endoscopy': 'Internal examination image',
            'clinical_photograph': 'Clinical photo',
            'medical_radiograph': 'Medical X-ray',
            'radiological_scan': 'Medical scan',
            'high_resolution_clinical_image': 'High-quality clinical photo',
            'medical_document': 'Medical report or lab result',
            'lab_result_document': 'Laboratory test result',
            'microscopy_image': 'Microscopic image'
        }
        return friendly_names.get(medical_type, medical_type.replace('_', ' ').title())

    def _generate_clinical_context(self, medical_type: str, analysis: Dict[str, Any]) -> str:
        """
        Generate condition-aware clinical context description based on image type and findings.

        This improved version provides appropriate context that doesn't unnecessarily alarm
        patients with pathological language for normal findings.
        """
        # Get pathological analysis for condition-aware context
        medical_context = analysis.get('medical_context', {})
        pathological_analysis = medical_context.get('pathological_analysis', {})
        has_pathological_findings = pathological_analysis.get('has_pathological_findings', False)
        clinical_significance = pathological_analysis.get('clinical_significance', 'routine_documentation')

        # Base clinical contexts - neutral language
        base_contexts = {
            'chest_xray': 'for pulmonary and cardiac imaging',
            'computed_tomography': 'for detailed cross-sectional imaging',
            'magnetic_resonance': 'for soft tissue and organ imaging',
            'ultrasound': 'for real-time imaging assessment',
            'mammography': 'for breast health screening',
            'dermatological_image': 'for skin documentation',
            'retinal_image': 'for eye health examination',
            'pathological_image': 'for histological analysis',
            'endoscopy': 'for internal examination',
            'clinical_photograph': 'for clinical documentation',
            'medical_document': 'containing clinical information',
            'lab_result_document': 'containing laboratory test results'
        }

        base_context = base_contexts.get(medical_type, 'for medical documentation')

        # Modify context based on clinical significance
        if clinical_significance == 'routine_documentation' or clinical_significance == 'routine_skin_documentation':
            if medical_type == 'dermatological_image':
                context = 'for routine skin health documentation'
            elif medical_type in ['chest_xray', 'computed_tomography', 'magnetic_resonance']:
                context = 'for routine health screening'
            else:
                context = base_context
        elif clinical_significance == 'screening_examination':
            context = f"{base_context} and health screening"
        elif clinical_significance == 'condition_monitoring':
            if medical_type == 'dermatological_image':
                context = 'for skin condition monitoring and care'
            else:
                context = f"{base_context} and condition monitoring"
        elif clinical_significance == 'follow_up_recommended':
            context = f"{base_context} with follow-up recommended"
        elif clinical_significance == 'professional_review_recommended':
            context = f"{base_context} for professional assessment"
        elif clinical_significance == 'pathological_examination':
            context = f"{base_context} and diagnostic analysis"
        else:
            context = base_context

        # Add specific context based on DICOM metadata
        if analysis.get('is_dicom', False):
            body_part = analysis.get('body_part_examined', '')
            if body_part and body_part != 'Unknown':
                return f"{context} of {body_part.lower()}"

        return context

    def _extract_comprehensive_medical_indicators(self, analysis: Dict[str, Any],
                                                medical_context: Dict[str, Any]) -> List[str]:
        """Extract comprehensive medical indicators from analysis."""
        indicators = []

        # Filename-based indicators
        filename_indicators = medical_context.get('filename_indicators', [])
        indicators.extend(filename_indicators)

        # Content-based indicators
        image_chars = medical_context.get('image_characteristics', {})

        # Add imaging quality indicators
        if image_chars.get('has_high_contrast', False):
            indicators.append('high contrast imaging')

        if image_chars.get('has_dark_background', False):
            indicators.append('radiological imaging')

        # Add specialty-specific indicators
        medical_type = analysis.get('medical_type', '')
        if 'dermatological' in medical_type:
            skin_likelihood = image_chars.get('skin_tone_likelihood', 0)
            if skin_likelihood > 0.5:
                indicators.append('skin tissue visible')

        if 'pathological' in medical_type:
            if image_chars.get('texture_complexity', 0) > 1.5:
                indicators.append('microscopic detail')

        # Remove duplicates and return
        return list(set(indicators))

    def _get_confidence_description(self, relevance_score: float, analysis: Dict[str, Any]) -> str:
        """Generate confidence description for medical classification."""
        if relevance_score > 0.8:
            return "High confidence medical classification"
        elif relevance_score > 0.6:
            return "Good confidence medical classification"
        elif relevance_score > 0.4:
            return "Moderate confidence medical classification"
        elif analysis.get('is_dicom', False):
            return "DICOM medical imaging standard"
        else:
            return None

    def _generate_medical_keywords(self, medical_type: str, analysis: Dict[str, Any]) -> List[str]:
        """
        Generate condition-aware medical keywords for enhanced RAG searchability.

        This improved version avoids inappropriate pathological terms for normal findings
        and generates contextually appropriate keywords based on actual image analysis.
        """
        keywords = []

        # Get pathological analysis for condition-aware keyword generation
        medical_context = analysis.get('medical_context', {})
        pathological_analysis = medical_context.get('pathological_analysis', {})
        has_pathological_findings = pathological_analysis.get('has_pathological_findings', False)
        clinical_significance = pathological_analysis.get('clinical_significance', 'routine_documentation')
        specific_findings = pathological_analysis.get('specific_findings', [])
        normal_indicators = pathological_analysis.get('normal_indicators', [])

        # Base keywords by type - neutral terms that don't imply pathology
        base_type_keywords = {
            'chest_xray': ['radiology', 'pulmonary imaging', 'cardiac imaging', 'thoracic imaging', 'respiratory system'],
            'computed_tomography': ['radiology', 'cross-sectional imaging', 'diagnostic imaging', 'CT imaging'],
            'magnetic_resonance': ['radiology', 'soft tissue imaging', 'MRI imaging', 'diagnostic imaging'],
            'ultrasound': ['sonography', 'real-time imaging', 'diagnostic ultrasound', 'medical imaging'],
            'mammography': ['breast imaging', 'women\'s health', 'preventive screening'],
            'dermatological_image': ['dermatology', 'skin imaging', 'skin documentation'],
            'retinal_image': ['ophthalmology', 'eye examination', 'retinal imaging', 'vision assessment'],
            'pathological_image': ['pathology', 'histology', 'tissue analysis', 'microscopy'],
            'endoscopy': ['gastroenterology', 'internal examination', 'endoscopic imaging'],
            'clinical_photograph': ['clinical documentation', 'medical photography'],
            'medical_document': ['clinical documentation', 'medical record', 'patient information'],
            'lab_result_document': ['laboratory', 'diagnostic testing', 'clinical chemistry']
        }

        # Add base keywords
        keywords.extend(base_type_keywords.get(medical_type, ['medical imaging', 'clinical documentation']))

        # Add condition-specific keywords based on pathological analysis
        if has_pathological_findings:
            # Only add pathological terms when there are actual findings
            if medical_type == 'dermatological_image':
                keywords.extend(self._get_dermatological_pathology_keywords(specific_findings))
            elif medical_type in ['chest_xray', 'computed_tomography', 'magnetic_resonance', 'radiological_scan']:
                keywords.extend(self._get_radiological_pathology_keywords(specific_findings))
            elif medical_type == 'clinical_photograph':
                keywords.extend(self._get_clinical_pathology_keywords(specific_findings))
        else:
            # Add normal/routine keywords for baseline findings
            if medical_type == 'dermatological_image':
                keywords.extend(['baseline skin documentation', 'natural skin appearance', 'skin documentation'])
            elif medical_type in ['chest_xray', 'computed_tomography', 'magnetic_resonance', 'radiological_scan']:
                keywords.extend(['routine imaging', 'screening examination', 'preventive care'])
            elif medical_type == 'clinical_photograph':
                keywords.extend(['routine documentation', 'clinical photography', 'medical record'])

        # Add clinical significance keywords
        significance_keywords = {
            'routine_documentation': ['routine care', 'documentation'],
            'routine_skin_documentation': ['skin health', 'routine dermatology'],
            'screening_examination': ['preventive care', 'health screening'],
            'condition_monitoring': ['medical monitoring', 'follow-up care'],
            'follow_up_recommended': ['clinical follow-up', 'medical review'],
            'professional_review_recommended': ['professional assessment', 'clinical evaluation'],
            'pathological_examination': ['diagnostic analysis', 'pathological assessment']
        }

        if clinical_significance in significance_keywords:
            keywords.extend(significance_keywords[clinical_significance])

        # Add normal indicators as positive keywords
        if normal_indicators:
            normal_keyword_mapping = {
                'uniform_coloration': ['normal pigmentation', 'natural skin appearance'],
                'consistent_pigmentation': ['baseline skin documentation', 'consistent skin appearance'],
                'smooth_texture': ['normal skin texture', 'natural skin surface'],
                'normal_texture': ['normal skin texture'],
                'no_obvious_lesions': ['clear skin appearance', 'no visible abnormalities'],
                'routine_imaging': ['standard imaging', 'routine examination'],
                'clinical_documentation': ['medical documentation']
            }

            for indicator in normal_indicators:
                if indicator in normal_keyword_mapping:
                    keywords.extend(normal_keyword_mapping[indicator])

        # Add DICOM-specific keywords
        if analysis.get('is_dicom', False):
            keywords.extend(['DICOM', 'medical imaging standard', 'digital imaging'])

            modality = analysis.get('modality', '')
            if modality:
                keywords.append(f'{modality} imaging')

        # Add quality keywords
        if analysis.get('width', 0) >= 1024 or analysis.get('height', 0) >= 1024:
            keywords.append('high resolution')

        if analysis.get('is_grayscale', False):
            keywords.append('grayscale imaging')
        else:
            keywords.append('color imaging')

        # Apply comprehensive deduplication and prioritization
        return self._deduplicate_and_prioritize_keywords(keywords)

    def _get_dermatological_pathology_keywords(self, specific_findings: List[str]) -> List[str]:
        """Generate pathological keywords for dermatological images with actual findings."""
        pathology_keywords = []

        finding_keywords = {
            'color_variation': ['pigmentation changes', 'color irregularity'],
            'dark_regions': ['hyperpigmentation', 'dark spots'],
            'bright_regions': ['hypopigmentation', 'light spots'],
            'defined_borders': ['lesion borders', 'skin lesion'],
            'texture_irregularity': ['skin texture changes', 'surface irregularity'],
            'potential_lesions': ['skin lesion', 'dermatological finding']
        }

        for finding in specific_findings:
            if finding in finding_keywords:
                pathology_keywords.extend(finding_keywords[finding])

        # Only add general pathological terms if specific findings are present
        if pathology_keywords:
            pathology_keywords.extend(['dermatological condition', 'skin condition monitoring'])

        return pathology_keywords

    def _get_radiological_pathology_keywords(self, specific_findings: List[str]) -> List[str]:
        """Generate pathological keywords for radiological images with actual findings."""
        pathology_keywords = []

        finding_keywords = {
            'image_complexity': ['complex imaging', 'detailed examination'],
            'abnormal_density': ['density changes', 'radiological finding'],
            'structural_changes': ['anatomical changes', 'structural abnormality']
        }

        for finding in specific_findings:
            if finding in finding_keywords:
                pathology_keywords.extend(finding_keywords[finding])

        if pathology_keywords:
            pathology_keywords.extend(['diagnostic imaging', 'radiological assessment'])

        return pathology_keywords

    def _get_clinical_pathology_keywords(self, specific_findings: List[str]) -> List[str]:
        """Generate pathological keywords for clinical photographs with actual findings."""
        pathology_keywords = []

        finding_keywords = {
            'visual_variation': ['clinical variation', 'visual changes'],
            'color_changes': ['appearance changes', 'clinical finding'],
            'structural_changes': ['anatomical variation', 'clinical observation']
        }

        for finding in specific_findings:
            if finding in finding_keywords:
                pathology_keywords.extend(finding_keywords[finding])

        if pathology_keywords:
            pathology_keywords.extend(['clinical assessment', 'medical observation'])

        return pathology_keywords

    def _deduplicate_and_prioritize_keywords(self, keywords: List[str]) -> List[str]:
        """
        Comprehensive keyword deduplication and prioritization system.

        Removes redundant terms and prioritizes the most relevant medical keywords
        to address user feedback about repeated terms like "routine", "high resolution", "grayscale".
        """
        try:
            # Define keyword priority levels (higher number = higher priority)
            keyword_priorities = {
                # High priority - specific medical terms
                'dermatology': 5, 'radiology': 5, 'pathology': 5, 'ophthalmology': 5,
                'skin lesion': 5, 'chest imaging': 5, 'diagnostic imaging': 5,
                'condition_monitoring': 5, 'follow_up_recommended': 5,
                'thoracic imaging': 5, 'pulmonary imaging': 5, 'cardiac imaging': 5,
                'respiratory system': 5,

                # Medium-high priority - clinical significance
                'clinical assessment': 4, 'medical review': 4, 'professional assessment': 4,
                'skin documentation': 4, 'medical monitoring': 4,
                'pigmentation changes': 4, 'color irregularity': 4,
                'health screening': 4, 'preventive care': 4,

                # Medium priority - general medical terms
                'medical imaging': 3, 'clinical documentation': 3, 'skin imaging': 3,
                'screening examination': 3,

                # Lower priority - technical descriptors (often redundant)
                'high resolution': 2, 'grayscale imaging': 2, 'color imaging': 2,
                'routine care': 2, 'documentation': 2, 'routine imaging': 2,
                'standard imaging': 2,

                # Lowest priority - very common terms (often redundant)
                'routine': 1, 'standard': 1, 'normal': 1, 'baseline': 1
            }

            # Define redundancy groups - if multiple keywords from same group exist, keep only the highest priority
            redundancy_groups = {
                'resolution': ['high resolution', 'resolution', 'imaging quality'],
                'routine_terms': ['routine', 'routine care', 'routine examination', 'routine imaging', 'standard imaging', 'baseline documentation'],
                'imaging_type': ['grayscale imaging', 'color imaging', 'medical imaging', 'clinical imaging'],
                'documentation': ['documentation', 'clinical documentation', 'medical documentation'],
                'skin_health': ['skin health', 'skin documentation', 'skin imaging'],
                'normal_terms': ['normal', 'healthy', 'baseline', 'standard'],
                'examination_type': ['screening examination', 'routine examination', 'health screening', 'preventive care']
            }

            # Step 1: Remove exact duplicates
            unique_keywords = list(dict.fromkeys(keywords))  # Preserves order

            # Step 2: Handle redundancy groups
            final_keywords = []
            used_groups = set()

            for keyword in unique_keywords:
                # Check if this keyword belongs to any redundancy group
                keyword_group = None
                for group_name, group_keywords in redundancy_groups.items():
                    if keyword in group_keywords:
                        keyword_group = group_name
                        break

                if keyword_group:
                    if keyword_group not in used_groups:
                        # Find the highest priority keyword in this group that exists in our list
                        group_candidates = [kw for kw in unique_keywords if kw in redundancy_groups[keyword_group]]
                        if group_candidates:
                            # Sort by priority (highest first)
                            best_keyword = max(group_candidates,
                                             key=lambda x: keyword_priorities.get(x, 0))
                            final_keywords.append(best_keyword)
                            used_groups.add(keyword_group)
                else:
                    # Not in any redundancy group, add directly
                    final_keywords.append(keyword)

            # Step 2.5: Additional filtering for substring redundancy
            # Remove keywords that are substrings of higher priority keywords
            filtered_keywords = []
            for keyword in final_keywords:
                is_redundant = False
                for other_keyword in final_keywords:
                    if (keyword != other_keyword and
                        keyword in other_keyword and
                        keyword_priorities.get(keyword, 0) <= keyword_priorities.get(other_keyword, 0)):
                        is_redundant = True
                        break
                if not is_redundant:
                    filtered_keywords.append(keyword)

            final_keywords = filtered_keywords

            # Step 3: Sort by priority and limit total count
            final_keywords = sorted(set(final_keywords),
                                  key=lambda x: keyword_priorities.get(x, 0),
                                  reverse=True)

            # Step 4: Limit to reasonable number of keywords (max 15)
            return final_keywords[:15]

        except Exception as e:
            logger.warning(f"Error in keyword deduplication: {e}")
            # Fallback to simple deduplication
            return list(dict.fromkeys(keywords))[:15]