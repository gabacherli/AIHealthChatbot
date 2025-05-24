# Medical Image Validation Test Directory

This directory is organized to help you systematically test the enhanced medical image classification system.

## Directory Structure:

### 📁 chest_xrays/
- Place chest X-ray images here
- Supported formats: .jpg, .jpeg, .png, .dcm, .dicom
- Examples: chest_pa.jpg, chest_lateral.dcm

### 📁 ct_scans/
- Place CT scan images here
- Both DICOM and standard image formats supported
- Examples: ct_head.dcm, ct_abdomen.jpg

### 📁 mri_images/
- Place MRI images here
- T1, T2, FLAIR, DWI sequences welcome
- Examples: mri_brain_t1.dcm, mri_spine.jpg

### 📁 ultrasounds/
- Place ultrasound images here
- Abdominal, cardiac, obstetric ultrasounds
- Examples: us_abdomen.jpg, echo_heart.dcm

### 📁 dicom_files/
- Place any DICOM files here for DICOM-specific testing
- Will test DICOM metadata extraction
- Examples: any .dcm or .dicom files

### 📁 mammography/
- Place mammography images here
- Digital mammograms, tomosynthesis
- Examples: mammo_cc.dcm, mammo_mlo.jpg

### 📁 clinical_photos/
- Place clinical photographs here
- Wound photos, skin lesions, etc.
- Examples: wound_day1.jpg, lesion_dermoscopy.png

### 📁 pathology_images/
- Place histology/pathology images here
- Microscopy images, tissue samples
- Examples: h_e_slide.jpg, immunostain.tiff

### 📁 retinal_images/
- Place ophthalmology images here
- Fundus photos, OCT images
- Examples: fundus_od.jpg, oct_macula.png

### 📁 dermatology_images/
- Place dermatological images here
- Skin lesions, rashes, etc.
- Examples: melanoma.jpg, rash_arm.png

### 📁 other_medical/
- Place any other medical images here
- Endoscopy, nuclear medicine, etc.
- Examples: endoscopy_colon.jpg, pet_scan.dcm

## Supported File Formats:
- Standard images: .jpg, .jpeg, .png, .bmp, .tiff, .tif
- DICOM files: .dcm, .dicom, .ima, .img

## Naming Conventions (Optional but Helpful):
- Include medical terms in filenames for better testing
- Examples:
  - chest_xray_pa.jpg
  - ct_brain_axial.dcm
  - mri_knee_t2.jpg
  - us_gallbladder.png

## Running Validation:
1. Add your medical images to the appropriate subdirectories
2. Run: python medical_image_validation.py
3. Follow the interactive prompts to validate classifications
4. Review results in the validation_results/ directory

## Tips:
- Start with a small set of images (5-10) to test the workflow
- Include both DICOM and standard image formats
- Mix different medical image types for comprehensive testing
- Use clear, descriptive filenames when possible
