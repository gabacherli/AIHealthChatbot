"""
Education level constants for the Health Chatbot application.
These constants define the standardized education levels used throughout the system.
"""

from typing import List, Dict

# Valid education levels (must match the ENUM in the database)
VALID_EDUCATION_LEVELS = [
    'elementary_school',
    'middle_school', 
    'high_school',
    'associate_degree',
    'bachelor_degree',
    'master_degree',
    'doctoral_degree',
    'professional_degree',  # MD, JD, PharmD, etc.
    'other'
]

# Human-readable labels for education levels
EDUCATION_LEVEL_LABELS = {
    'elementary_school': 'Elementary School',
    'middle_school': 'Middle School',
    'high_school': 'High School',
    'associate_degree': 'Associate Degree',
    'bachelor_degree': 'Bachelor Degree',
    'master_degree': 'Master Degree',
    'doctoral_degree': 'Doctoral Degree (PhD)',
    'professional_degree': 'Professional Degree (MD, JD, etc.)',
    'other': 'Other'
}

# Education levels grouped by complexity for prompt customization
EDUCATION_COMPLEXITY_GROUPS = {
    'basic': ['elementary_school', 'middle_school', 'high_school'],
    'undergraduate': ['associate_degree', 'bachelor_degree'],
    'graduate': ['master_degree', 'doctoral_degree'],
    'professional': ['professional_degree'],
    'other': ['other']
}

# Reverse mapping for complexity lookup
EDUCATION_TO_COMPLEXITY = {}
for complexity, levels in EDUCATION_COMPLEXITY_GROUPS.items():
    for level in levels:
        EDUCATION_TO_COMPLEXITY[level] = complexity


def validate_education_level(level: str) -> bool:
    """
    Validate if an education level is valid.
    
    Args:
        level: Education level to validate
        
    Returns:
        True if valid, False otherwise
    """
    return level in VALID_EDUCATION_LEVELS


def get_education_complexity(level: str) -> str:
    """
    Get the complexity group for an education level.
    
    Args:
        level: Education level
        
    Returns:
        Complexity group ('basic', 'undergraduate', 'graduate', 'professional', 'other')
    """
    return EDUCATION_TO_COMPLEXITY.get(level, 'other')


def get_education_label(level: str) -> str:
    """
    Get the human-readable label for an education level.
    
    Args:
        level: Education level
        
    Returns:
        Human-readable label
    """
    return EDUCATION_LEVEL_LABELS.get(level, 'Unknown')


def get_all_education_options() -> List[Dict[str, str]]:
    """
    Get all education level options for UI dropdowns.
    
    Returns:
        List of dictionaries with 'value' and 'label' keys
    """
    return [
        {'value': level, 'label': EDUCATION_LEVEL_LABELS[level]}
        for level in VALID_EDUCATION_LEVELS
    ]
