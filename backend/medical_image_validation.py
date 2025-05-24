#!/usr/bin/env python3
"""
Comprehensive Medical Image Classification Validation Framework

This script provides an interactive testing workflow for validating the enhanced
medical image classification system with real medical image samples.
"""

import os
import sys
import json
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import shutil

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.medical_image_classifier import MedicalImageClassifier
from utils.document_processor import DocumentProcessor
# Note: MedicalEmbeddingService import removed to avoid dependency issues in standalone validation

class MedicalImageValidator:
    """Interactive medical image classification validator."""

    def __init__(self, test_images_dir: str = "test_medical_images", results_dir: str = "validation_results"):
        """
        Initialize the validator.

        Args:
            test_images_dir: Directory containing test medical images
            results_dir: Directory to store validation results
        """
        self.test_images_dir = Path(test_images_dir)
        self.results_dir = Path(results_dir)

        # Create directories if they don't exist
        self.test_images_dir.mkdir(exist_ok=True)
        self.results_dir.mkdir(exist_ok=True)

        # Initialize components
        self.classifier = MedicalImageClassifier()
        self.document_processor = DocumentProcessor()
        # Note: MedicalEmbeddingService not initialized to avoid dependency issues

        # Validation results
        self.validation_results = []
        self.session_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Supported image extensions
        self.supported_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif',
                                   '.dcm', '.dicom', '.ima', '.img'}

        print(f"🏥 Medical Image Classification Validator Initialized")
        print(f"📁 Test images directory: {self.test_images_dir.absolute()}")
        print(f"📊 Results directory: {self.results_dir.absolute()}")
        print(f"🆔 Session ID: {self.session_id}")

    def setup_test_environment(self):
        """Set up the test environment and provide instructions."""
        print("\n" + "="*80)
        print("🔧 MEDICAL IMAGE VALIDATION SETUP")
        print("="*80)

        print(f"\n📋 INSTRUCTIONS:")
        print(f"1. Place your medical image samples in: {self.test_images_dir.absolute()}")
        print(f"2. Supported formats: {', '.join(sorted(self.supported_extensions))}")
        print(f"3. Organize images by type (optional) using subdirectories:")
        print(f"   - chest_xrays/")
        print(f"   - ct_scans/")
        print(f"   - mri_images/")
        print(f"   - ultrasounds/")
        print(f"   - dicom_files/")
        print(f"   - clinical_photos/")
        print(f"   - other/")

        print(f"\n📁 Current test directory contents:")
        if self.test_images_dir.exists():
            image_files = self.get_test_images()
            if image_files:
                for i, img_path in enumerate(image_files[:10], 1):  # Show first 10
                    print(f"   {i}. {img_path.name}")
                if len(image_files) > 10:
                    print(f"   ... and {len(image_files) - 10} more files")
                print(f"\n✅ Found {len(image_files)} test images")
            else:
                print("   (No image files found)")
                print(f"\n⚠️  Please add medical image samples to {self.test_images_dir.absolute()}")

        return len(self.get_test_images()) > 0

    def get_test_images(self) -> List[Path]:
        """Get list of test image files."""
        image_files = []
        for ext in self.supported_extensions:
            image_files.extend(self.test_images_dir.rglob(f"*{ext}"))
        return sorted(image_files)

    def analyze_single_image(self, image_path: Path) -> Dict[str, Any]:
        """Analyze a single medical image and return comprehensive results."""
        print(f"\n🔍 Analyzing: {image_path.name}")

        try:
            # Read image file
            with open(image_path, 'rb') as f:
                image_bytes = f.read()

            # Get file info
            file_info = {
                'filename': image_path.name,
                'file_size': len(image_bytes),
                'file_path': str(image_path.relative_to(self.test_images_dir)),
                'file_extension': image_path.suffix.lower()
            }

            # Classify with enhanced medical classifier
            classification_result = self.classifier.analyze_medical_image(image_bytes, image_path.name)

            # Generate medical description
            medical_description = self.classifier.create_medical_description(image_path.name, classification_result)

            # Process with document processor (simulates full pipeline)
            doc_chunks = self.document_processor._process_image_bytes(image_bytes, image_path.name)

            # Prepare comprehensive results
            analysis_result = {
                'file_info': file_info,
                'classification': classification_result,
                'medical_description': medical_description,
                'document_chunks': len(doc_chunks),
                'chunk_content': doc_chunks[0]['content'] if doc_chunks else None,
                'timestamp': datetime.datetime.now().isoformat()
            }

            return analysis_result

        except Exception as e:
            print(f"❌ Error analyzing {image_path.name}: {e}")
            return {
                'file_info': {'filename': image_path.name, 'error': str(e)},
                'classification': {'analysis_error': str(e)},
                'medical_description': f"Error analyzing {image_path.name}",
                'timestamp': datetime.datetime.now().isoformat()
            }

    def display_analysis_results(self, result: Dict[str, Any]):
        """Display analysis results in a clear, reviewable format."""
        print("\n" + "="*60)
        print("📊 MEDICAL IMAGE ANALYSIS RESULTS")
        print("="*60)

        # File Information
        file_info = result.get('file_info', {})
        print(f"\n📁 FILE INFORMATION:")
        print(f"   Filename: {file_info.get('filename', 'Unknown')}")
        print(f"   File Path: {file_info.get('file_path', 'Unknown')}")
        print(f"   File Size: {file_info.get('file_size', 0):,} bytes")
        print(f"   Extension: {file_info.get('file_extension', 'Unknown')}")

        # Classification Results
        classification = result.get('classification', {})
        print(f"\n🏥 MEDICAL CLASSIFICATION:")
        print(f"   Medical Type: {classification.get('medical_type', 'Unknown')}")
        print(f"   Is DICOM: {classification.get('is_dicom', False)}")

        if classification.get('is_dicom', False):
            print(f"   DICOM Modality: {classification.get('modality', 'Unknown')}")
            print(f"   Body Part: {classification.get('body_part_examined', 'Unknown')}")
            print(f"   Study Description: {classification.get('study_description', 'N/A')}")
            print(f"   Series Description: {classification.get('series_description', 'N/A')}")

        # Image Properties
        if 'width' in classification and 'height' in classification:
            print(f"   Dimensions: {classification['width']}x{classification['height']}")
        print(f"   Is Grayscale: {classification.get('is_grayscale', 'Unknown')}")
        print(f"   Aspect Ratio: {classification.get('aspect_ratio', 'Unknown')}")

        # Medical Context
        medical_context = classification.get('medical_context', {})
        if medical_context:
            print(f"\n🎯 MEDICAL CONTEXT:")
            print(f"   Relevance Score: {medical_context.get('medical_relevance_score', 'Unknown')}")
            filename_indicators = medical_context.get('filename_indicators', [])
            if filename_indicators:
                print(f"   Filename Indicators: {', '.join(filename_indicators)}")

            # Image characteristics
            img_chars = medical_context.get('image_characteristics', {})
            if img_chars:
                mean_intensity = img_chars.get('mean_intensity', 'N/A')
                contrast_ratio = img_chars.get('contrast_ratio', 'N/A')

                if isinstance(mean_intensity, (int, float)):
                    print(f"   Mean Intensity: {mean_intensity:.2f}")
                else:
                    print(f"   Mean Intensity: {mean_intensity}")

                if isinstance(contrast_ratio, (int, float)):
                    print(f"   Contrast Ratio: {contrast_ratio:.3f}")
                else:
                    print(f"   Contrast Ratio: {contrast_ratio}")

        # Medical Description
        description = result.get('medical_description', '')
        print(f"\n📝 MEDICAL DESCRIPTION:")
        print(f"   {description}")

        # Error Information
        if 'analysis_error' in classification:
            print(f"\n⚠️  ANALYSIS ERROR:")
            print(f"   {classification['analysis_error']}")

    def get_user_feedback(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Get user feedback on the classification results."""
        print(f"\n" + "="*60)
        print("💬 VALIDATION FEEDBACK")
        print("="*60)

        feedback = {}

        # Overall accuracy
        while True:
            accuracy = input("\n✅ Is the medical type classification CORRECT? (y/n/s to skip): ").lower().strip()
            if accuracy in ['y', 'yes', 'n', 'no', 's', 'skip']:
                feedback['classification_correct'] = accuracy in ['y', 'yes']
                feedback['skipped'] = accuracy in ['s', 'skip']
                break
            print("Please enter 'y' for yes, 'n' for no, or 's' to skip")

        if not feedback.get('skipped', False):
            # If incorrect, get correct classification
            if not feedback['classification_correct']:
                correct_type = input("🔧 What is the CORRECT medical image type? ").strip()
                feedback['correct_medical_type'] = correct_type

            # DICOM feedback
            is_dicom = result.get('classification', {}).get('is_dicom', False)
            dicom_feedback = input(f"📋 Is DICOM detection correct? (Currently: {is_dicom}) (y/n/s): ").lower().strip()
            if dicom_feedback in ['y', 'yes']:
                feedback['dicom_correct'] = True
            elif dicom_feedback in ['n', 'no']:
                feedback['dicom_correct'] = False
                feedback['correct_is_dicom'] = not is_dicom

            # Description quality
            desc_quality = input("📝 Rate the medical description quality (1-5, 5=excellent): ").strip()
            try:
                feedback['description_quality'] = int(desc_quality)
            except ValueError:
                feedback['description_quality'] = None

            # Additional comments
            comments = input("💭 Additional comments (optional): ").strip()
            if comments:
                feedback['comments'] = comments

        feedback['timestamp'] = datetime.datetime.now().isoformat()
        return feedback

    def save_validation_result(self, result: Dict[str, Any], feedback: Dict[str, Any]):
        """Save validation result with feedback."""
        try:
            validation_entry = {
                'session_id': self.session_id,
                'analysis_result': result,
                'user_feedback': feedback,
                'validation_timestamp': datetime.datetime.now().isoformat()
            }

            self.validation_results.append(validation_entry)

            # Save individual result file
            filename = result['file_info']['filename']
            safe_filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
            result_file = self.results_dir / f"{self.session_id}_{safe_filename}_result.json"

            # Convert numpy types to native Python types for JSON serialization
            def convert_numpy_types(obj):
                if hasattr(obj, 'item'):  # numpy scalar
                    return obj.item()
                elif hasattr(obj, 'tolist'):  # numpy array
                    return obj.tolist()
                elif isinstance(obj, dict):
                    return {k: convert_numpy_types(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_numpy_types(v) for v in obj]
                else:
                    return obj

            # Clean the validation entry for JSON serialization
            clean_entry = convert_numpy_types(validation_entry)

            with open(result_file, 'w') as f:
                json.dump(clean_entry, f, indent=2)

            print(f"✅ Result saved: {result_file.name}")

        except Exception as e:
            print(f"⚠️  Error saving result: {e}")
            # Continue execution even if saving fails

    def generate_validation_report(self):
        """Generate comprehensive validation report."""
        if not self.validation_results:
            print("⚠️  No validation results to report")
            return

        report_file = self.results_dir / f"{self.session_id}_validation_report.json"
        summary_file = self.results_dir / f"{self.session_id}_validation_summary.txt"

        # Calculate statistics
        total_images = len(self.validation_results)
        correct_classifications = sum(1 for r in self.validation_results
                                    if r['user_feedback'].get('classification_correct', False))
        skipped = sum(1 for r in self.validation_results
                     if r['user_feedback'].get('skipped', False))

        # Medical type distribution
        medical_types = {}
        dicom_accuracy = {'correct': 0, 'total': 0}
        description_ratings = []

        for result in self.validation_results:
            if not result['user_feedback'].get('skipped', False):
                # Medical type distribution
                med_type = result['analysis_result']['classification'].get('medical_type', 'unknown')
                medical_types[med_type] = medical_types.get(med_type, 0) + 1

                # DICOM accuracy
                if 'dicom_correct' in result['user_feedback']:
                    dicom_accuracy['total'] += 1
                    if result['user_feedback']['dicom_correct']:
                        dicom_accuracy['correct'] += 1

                # Description quality
                quality = result['user_feedback'].get('description_quality')
                if quality is not None:
                    description_ratings.append(quality)

        # Generate summary report
        summary = f"""
MEDICAL IMAGE CLASSIFICATION VALIDATION REPORT
Session ID: {self.session_id}
Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

OVERALL STATISTICS:
- Total Images Processed: {total_images}
- Correct Classifications: {correct_classifications}/{total_images - skipped} ({(correct_classifications/(total_images-skipped)*100) if total_images > skipped else 0:.1f}%)
- Skipped Images: {skipped}

MEDICAL TYPE DISTRIBUTION:
"""
        for med_type, count in sorted(medical_types.items()):
            summary += f"- {med_type}: {count} images\n"

        if dicom_accuracy['total'] > 0:
            dicom_acc_pct = (dicom_accuracy['correct'] / dicom_accuracy['total']) * 100
            summary += f"\nDICOM DETECTION ACCURACY: {dicom_accuracy['correct']}/{dicom_accuracy['total']} ({dicom_acc_pct:.1f}%)\n"

        if description_ratings:
            avg_rating = sum(description_ratings) / len(description_ratings)
            summary += f"\nDESCRIPTION QUALITY: Average {avg_rating:.1f}/5.0 ({len(description_ratings)} ratings)\n"

        # Save detailed report
        detailed_report = {
            'session_info': {
                'session_id': self.session_id,
                'generated_at': datetime.datetime.now().isoformat(),
                'total_images': total_images,
                'correct_classifications': correct_classifications,
                'skipped_images': skipped
            },
            'statistics': {
                'classification_accuracy': (correct_classifications/(total_images-skipped)) if total_images > skipped else 0,
                'medical_type_distribution': medical_types,
                'dicom_accuracy': dicom_accuracy,
                'description_quality': {
                    'ratings': description_ratings,
                    'average': sum(description_ratings) / len(description_ratings) if description_ratings else None
                }
            },
            'detailed_results': self.validation_results
        }

        with open(report_file, 'w') as f:
            json.dump(detailed_report, f, indent=2)

        with open(summary_file, 'w') as f:
            f.write(summary)

        print(f"\n📊 VALIDATION REPORT GENERATED:")
        print(f"   Summary: {summary_file}")
        print(f"   Detailed: {report_file}")
        print(summary)

    def run_interactive_validation(self):
        """Run the interactive validation process."""
        print("\n" + "="*80)
        print("🚀 STARTING INTERACTIVE MEDICAL IMAGE VALIDATION")
        print("="*80)

        # Get test images
        test_images = self.get_test_images()
        if not test_images:
            print("❌ No test images found. Please add medical images to the test directory.")
            return

        print(f"\n📋 Found {len(test_images)} test images to validate")

        # Process each image
        for i, image_path in enumerate(test_images, 1):
            try:
                print(f"\n{'='*80}")
                print(f"🖼️  PROCESSING IMAGE {i}/{len(test_images)}")
                print(f"{'='*80}")

                # Analyze image
                result = self.analyze_single_image(image_path)

                # Display results
                self.display_analysis_results(result)

                # Get user feedback
                feedback = self.get_user_feedback(result)

                # Save result
                self.save_validation_result(result, feedback)

                # Check if user wants to continue
                if i < len(test_images):
                    continue_validation = input(f"\n⏭️  Continue to next image? (y/n/q to quit): ").lower().strip()
                    if continue_validation in ['n', 'no', 'q', 'quit']:
                        print(f"🛑 Validation stopped at user request ({i}/{len(test_images)} completed)")
                        break

            except KeyboardInterrupt:
                print(f"\n⚠️  Validation interrupted by user at image {i}")
                break
            except Exception as e:
                print(f"\n❌ Error processing image {image_path.name}: {e}")
                print("Continuing with next image...")
                continue

        # Generate final report
        print(f"\n{'='*80}")
        print("📊 GENERATING VALIDATION REPORT")
        print(f"{'='*80}")
        self.generate_validation_report()

def main():
    """Main validation function."""
    print("🏥 MEDICAL IMAGE CLASSIFICATION VALIDATION FRAMEWORK")
    print("="*80)

    # Initialize validator
    validator = MedicalImageValidator()

    # Setup test environment
    if not validator.setup_test_environment():
        print("\n❌ No test images found. Please add medical images and run again.")
        return

    # Confirm start
    start_validation = input(f"\n🚀 Start interactive validation? (y/n): ").lower().strip()
    if start_validation not in ['y', 'yes']:
        print("Validation cancelled.")
        return

    # Run validation
    try:
        validator.run_interactive_validation()
        print(f"\n✅ Validation completed successfully!")
        print(f"📁 Results saved in: {validator.results_dir.absolute()}")
    except KeyboardInterrupt:
        print(f"\n⚠️  Validation interrupted by user")
        if validator.validation_results:
            validator.generate_validation_report()
    except Exception as e:
        print(f"\n❌ Validation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
