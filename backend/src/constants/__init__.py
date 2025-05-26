"""
Constants module for the Health Chatbot application.
"""

from .education_levels import (
    VALID_EDUCATION_LEVELS,
    EDUCATION_LEVEL_LABELS,
    EDUCATION_COMPLEXITY_GROUPS,
    EDUCATION_TO_COMPLEXITY,
    validate_education_level,
    get_education_complexity,
    get_education_label,
    get_all_education_options
)

__all__ = [
    'VALID_EDUCATION_LEVELS',
    'EDUCATION_LEVEL_LABELS', 
    'EDUCATION_COMPLEXITY_GROUPS',
    'EDUCATION_TO_COMPLEXITY',
    'validate_education_level',
    'get_education_complexity',
    'get_education_label',
    'get_all_education_options'
]
