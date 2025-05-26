"""
Medical Disclaimer Service

This service handles post-processing of AI chatbot responses to append medical disclaimers
when documents have conflicting AI confidence indicators. This approach reduces token
consumption in the system prompt while maintaining the same medical disclaimer functionality.
"""

from typing import Dict, Any
import logging

try:
    from ..config import get_config
    from ..utils.medical_context_utils import has_conflicting_confidence
except ImportError:
    # Handle direct execution case
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from config import get_config
    from utils.medical_context_utils import has_conflicting_confidence

logger = logging.getLogger(__name__)
config = get_config()


def check_conflicting_confidence(img: Dict[str, Any]) -> bool:
    """
    Check if image has conflicting confidence indicators (high relevance + low pathological confidence).

    Args:
        img: Image data dictionary

    Returns:
        True if conflicting indicators found, False otherwise
    """
    try:
        return has_conflicting_confidence(
            img,
            relevance_threshold=config.MEDICAL_RELEVANCE_THRESHOLD,
            confidence_threshold=config.PATHOLOGICAL_CONFIDENCE_THRESHOLD
        )
    except Exception as e:
        logger.error(f"Error checking conflicting confidence for image {img.get('source', 'Unknown')}: {e}")
        return False


def _get_disclaimer_template(user_role: str, language: str = "pt") -> str:
    """
    Get the appropriate disclaimer template for the user role and language.

    Args:
        user_role: The role of the user (patient or professional)
        language: Language code ('pt' for Portuguese, 'en' for English)

    Returns:
        Disclaimer template string
    """
    if user_role == "patient":
        if language == "pt":
            return config.PATIENT_DISCLAIMER_TEMPLATE_PT
        else:
            return config.PATIENT_DISCLAIMER_TEMPLATE_EN
    else:
        if language == "pt":
            return config.PROFESSIONAL_DISCLAIMER_TEMPLATE_PT
        else:
            return config.PROFESSIONAL_DISCLAIMER_TEMPLATE_EN


def generate_medical_disclaimer(context_data: Dict[str, Any], user_role: str = "patient", language: str = "pt") -> str:
    """
    Generate medical disclaimer text for documents with conflicting AI confidence indicators.

    Args:
        context_data: Structured medical context data containing medical images
        user_role: The role of the user (patient or professional)
        language: Language code ('pt' for Portuguese, 'en' for English)

    Returns:
        Disclaimer text if conflicting confidence indicators are found, empty string otherwise
    """
    try:
        # Validate inputs
        if not context_data or not isinstance(context_data, dict):
            logger.debug("No context data provided for disclaimer generation")
            return ""

        if user_role not in ["patient", "professional"]:
            logger.warning(f"Invalid user role for disclaimer: {user_role}. Defaulting to 'patient'")
            user_role = "patient"

        # Check for conflicting confidence indicators across all images
        images = context_data.get("medical_images", [])
        if not images:
            logger.debug("No medical images found in context data")
            return ""

        conflicting_sources = []
        for img in images:
            try:
                if check_conflicting_confidence(img):
                    source = img.get('source', 'Unknown')
                    if source not in conflicting_sources:
                        conflicting_sources.append(source)
            except Exception as e:
                logger.warning(f"Error checking image {img.get('source', 'Unknown')} for conflicting confidence: {e}")
                continue

        # Generate disclaimer if there are conflicting confidence indicators
        if conflicting_sources:
            template = _get_disclaimer_template(user_role, language)
            disclaimer_text = template.format(sources=', '.join(conflicting_sources))

            logger.info(f"Generated medical disclaimer for {len(conflicting_sources)} documents with conflicting confidence (user_role: {user_role}, language: {language})")
            return disclaimer_text

        logger.debug("No conflicting confidence indicators found")
        return ""

    except Exception as e:
        logger.error(f"Error generating medical disclaimer: {e}")
        return ""


def append_medical_disclaimer(ai_response: str, context_data: Dict[str, Any], user_role: str = "patient", language: str = "pt") -> str:
    """
    Append medical disclaimer to AI chatbot response if conflicting confidence indicators are detected.

    Args:
        ai_response: The original AI chatbot response from OpenAI
        context_data: Structured medical context data containing medical images
        user_role: The role of the user (patient or professional)
        language: Language code ('pt' for Portuguese, 'en' for English)

    Returns:
        AI response with disclaimer appended if applicable, otherwise original response
    """
    try:
        # Validate AI response
        if not ai_response or not isinstance(ai_response, str):
            logger.warning("Invalid AI response provided for disclaimer processing")
            return ai_response or ""

        disclaimer = generate_medical_disclaimer(context_data, user_role, language)

        if disclaimer:
            # Append disclaimer to the end of the response with proper spacing
            enhanced_response = f"{ai_response}\n\n{disclaimer}"
            logger.debug(f"Appended medical disclaimer to AI response (length: {len(disclaimer)} chars)")
            return enhanced_response

        return ai_response

    except Exception as e:
        logger.error(f"Error appending medical disclaimer to AI response: {e}")
        return ai_response  # Return original response on error



