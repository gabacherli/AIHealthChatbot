"""
Medical Context Utilities

Shared utilities for parsing and extracting medical context data from document metadata.
This module consolidates common medical context parsing logic to avoid duplication.
"""

from typing import Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


def extract_medical_context(metadata: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Extract medical context from document metadata, handling both boolean and dict formats.
    
    Args:
        metadata: Document metadata dictionary
        
    Returns:
        Medical context dictionary if found, None otherwise
    """
    try:
        medical_context = metadata.get('medical_context')
        
        # Handle boolean medical_context (legacy format)
        if medical_context is True:
            image_info = metadata.get('image_info', {})
            if isinstance(image_info, dict):
                medical_context = image_info.get('medical_context', {})
        
        # Validate that we have a proper dictionary
        if medical_context and isinstance(medical_context, dict):
            return medical_context
            
        return None
        
    except Exception as e:
        logger.warning(f"Error extracting medical context from metadata: {e}")
        return None


def get_confidence_scores(medical_context: Dict[str, Any]) -> Tuple[float, float]:
    """
    Extract relevance score and pathological confidence from medical context.
    
    Args:
        medical_context: Medical context dictionary
        
    Returns:
        Tuple of (relevance_score, pathological_confidence)
    """
    try:
        # Get relevance score
        relevance_score = medical_context.get('medical_relevance_score', 0.0)
        
        # Get pathological confidence
        pathological_analysis = medical_context.get('pathological_analysis', {})
        pathological_confidence = 0.0
        
        if pathological_analysis and isinstance(pathological_analysis, dict):
            pathological_confidence = pathological_analysis.get('pathological_confidence', 0.0)
        
        return float(relevance_score), float(pathological_confidence)
        
    except Exception as e:
        logger.warning(f"Error extracting confidence scores: {e}")
        return 0.0, 0.0


def has_conflicting_confidence(img: Dict[str, Any], relevance_threshold: float = 0.8, 
                              confidence_threshold: float = 0.6) -> bool:
    """
    Check if image has conflicting confidence indicators.
    
    Args:
        img: Image data dictionary
        relevance_threshold: Minimum relevance score to consider high relevance
        confidence_threshold: Maximum pathological confidence to consider low confidence
        
    Returns:
        True if conflicting indicators found, False otherwise
    """
    try:
        metadata = img.get('metadata', {})
        medical_context = extract_medical_context(metadata)
        
        if not medical_context:
            return False
        
        relevance_score, pathological_confidence = get_confidence_scores(medical_context)
        
        # Check for conflicting indicators: high relevance + low pathological confidence
        return relevance_score >= relevance_threshold and pathological_confidence < confidence_threshold
        
    except Exception as e:
        logger.warning(f"Error checking conflicting confidence for image {img.get('source', 'Unknown')}: {e}")
        return False


def get_pathological_findings(medical_context: Dict[str, Any]) -> Tuple[list, list]:
    """
    Extract specific findings and normal indicators from medical context.
    
    Args:
        medical_context: Medical context dictionary
        
    Returns:
        Tuple of (specific_findings, normal_indicators)
    """
    try:
        pathological_analysis = medical_context.get('pathological_analysis', {})
        
        if not pathological_analysis or not isinstance(pathological_analysis, dict):
            return [], []
        
        specific_findings = pathological_analysis.get('specific_findings', [])
        normal_indicators = pathological_analysis.get('normal_indicators', [])
        
        # Ensure we return lists
        if not isinstance(specific_findings, list):
            specific_findings = [specific_findings] if specific_findings else []
        if not isinstance(normal_indicators, list):
            normal_indicators = [normal_indicators] if normal_indicators else []
            
        return specific_findings, normal_indicators
        
    except Exception as e:
        logger.warning(f"Error extracting pathological findings: {e}")
        return [], []
