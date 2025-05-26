"""
Template loader service for managing prompt templates.
This module provides functionality to load and manage prompt templates from files.
"""
import logging
from pathlib import Path
from typing import Optional
from functools import lru_cache

logger = logging.getLogger(__name__)

class TemplateLoader:
    """Service for loading and managing prompt templates."""

    def __init__(self, templates_dir: Optional[str] = None):
        """
        Initialize the template loader.

        Args:
            templates_dir: Path to the templates directory. If None, uses default.
        """
        if templates_dir is None:
            # Default to templates directory relative to this file
            current_dir = Path(__file__).parent
            self.templates_dir = current_dir.parent / "templates" / "prompts"
        else:
            self.templates_dir = Path(templates_dir)

        if not self.templates_dir.exists():
            logger.warning(f"Templates directory does not exist: {self.templates_dir}")

    @lru_cache(maxsize=32)
    def load_template(self, template_filename: str) -> str:
        """
        Load a template from file with caching.

        Args:
            template_filename: Full filename of the template file (including extension)

        Returns:
            Template content as string

        Raises:
            FileNotFoundError: If template file doesn't exist
            IOError: If template file cannot be read
        """
        template_path = self.templates_dir / template_filename

        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")

        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()

            logger.debug(f"Loaded template: {template_filename}")
            return content

        except IOError as e:
            logger.error(f"Error reading template {template_filename}: {e}")
            raise

    def get_patient_prompt(self, language: str = "pt") -> str:
        """
        Get patient assistant prompt in specified language.

        Args:
            language: Language code ('pt' for Portuguese, 'en' for English)

        Returns:
            Patient prompt template
        """
        if language == "pt":
            return self.load_template("patient_assistant_pt.md")
        else:
            return self.load_template("patient_assistant_en.md")

    def get_professional_prompt(self, context_type: str = "patient", language: str = "pt") -> str:
        """
        Get professional assistant prompt in specified language.

        Args:
            context_type: Type of context ("patient" or "your")
            language: Language code ('pt' for Portuguese, 'en' for English)

        Returns:
            Professional prompt template with context type formatted
        """
        if language == "pt":
            template = self.load_template("professional_assistant_pt.md")
        else:
            template = self.load_template("professional_assistant_en.md")
        return template.format(context_type=context_type)

    def get_no_context_prompt(self, user_role: str, is_professional_query: bool = False, language: str = "pt") -> str:
        """
        Get prompt for when no context documents are available.

        Args:
            user_role: Role of the user ("patient" or "professional")
            is_professional_query: Whether this is a professional querying patient data
            language: Language code ('pt' for Portuguese, 'en' for English)

        Returns:
            No-context prompt template
        """
        if user_role == "patient":
            if language == "pt":
                return self.load_template("patient_no_context_pt.md")
            else:
                return self.load_template("patient_no_context_en.md")
        else:
            if language == "pt":
                template = self.load_template("professional_no_context_pt.md")
                patient_note = "Nota: Nenhum documento específico do paciente estava disponível para esta consulta." if is_professional_query else ""
            else:
                template = self.load_template("professional_no_context_en.md")
                patient_note = "Note: No patient-specific documents were available for this query." if is_professional_query else ""
            return template.format(patient_note=patient_note)

    def clear_cache(self):
        """Clear the template cache."""
        self.load_template.cache_clear()
        logger.info("Template cache cleared")

    def list_available_templates(self) -> list:
        """
        List all available template files.

        Returns:
            List of template filenames (with extensions)
        """
        if not self.templates_dir.exists():
            return []

        templates = []
        for file_path in self.templates_dir.glob("*"):
            if file_path.is_file() and file_path.suffix in ['.md', '.txt']:
                templates.append(file_path.name)

        return sorted(templates)


# Global instance for easy access
template_loader = TemplateLoader()
