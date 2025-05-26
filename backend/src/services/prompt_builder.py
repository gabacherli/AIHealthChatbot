"""
Prompt builder service.
This module contains functions for building prompts for the OpenAI API.
"""
from typing import Dict, List, Any
import logging
from ..utils.medical_context_utils import extract_medical_context, get_pathological_findings
from .template_loader import template_loader

logger = logging.getLogger(__name__)

def build_prompt(question: str, context_data: Dict[str, Any], user_role: str, is_professional_query: bool = False, language: str = "pt"):
    """
    Build an enhanced prompt for the OpenAI API with medical context.

    Args:
        question: The user's question.
        context_data: Structured medical context data containing documents, keywords,
                     medical images, and pathological findings.
        user_role: The role of the user (patient or professional).
        is_professional_query: Whether this is a professional querying patient data.
        language: Language code ('pt' for Portuguese, 'en' for English). Defaults to 'pt'.

    Returns:
        A list of messages for the OpenAI API.
    """
    # Handle empty context
    if not context_data or not context_data.get("documents"):
        return _build_prompt_without_context(question, user_role, is_professional_query, language)

    # Build enhanced prompt with medical context
    return _build_enhanced_prompt(question, context_data, user_role, is_professional_query, language)


def _build_prompt_without_context(question: str, user_role: str, is_professional_query: bool, language: str = "pt"):
    """Build prompt when no context documents are available."""
    try:
        role_instruction = template_loader.get_no_context_prompt(user_role, is_professional_query, language=language)
    except (FileNotFoundError, IOError) as e:
        logger.warning(f"Failed to load template, using fallback: {e}")
        # Fallback to hardcoded prompts if template loading fails
        if user_role == "patient":
            if language == "pt":
                role_instruction = (
                    "Você é um assistente médico útil. Forneça informações gerais de saúde "
                    "em termos fáceis de entender adequados para um paciente. Sempre recomende "
                    "consultar profissionais de saúde para questões médicas específicas."
                )
            else:
                role_instruction = (
                    "You are a helpful medical assistant. Provide general health information "
                    "in easy-to-understand terms suitable for a patient. Always recommend "
                    "consulting with healthcare professionals for specific medical concerns."
                )
        else:
            if language == "pt":
                note = "Nota: Nenhum documento específico do paciente estava disponível para esta consulta." if is_professional_query else ""
                role_instruction = (
                    "Você é um assistente médico útil para profissionais de saúde. "
                    "Forneça insights clínicos detalhados e informações baseadas em evidências. "
                    f"{note}"
                )
            else:
                note = "Note: No patient-specific documents were available for this query." if is_professional_query else ""
                role_instruction = (
                    "You are a helpful medical assistant for healthcare professionals. "
                    "Provide detailed clinical insights and evidence-based information. "
                    f"{note}"
                )

    return [
        {"role": "system", "content": role_instruction},
        {"role": "user", "content": question},
    ]


def _build_enhanced_prompt(question: str, context_data: Dict[str, Any], user_role: str, is_professional_query: bool, language: str = "pt"):
    """Build enhanced prompt with medical context and metadata."""

    # Base role instructions
    try:
        if user_role == "patient":
            base_instruction = template_loader.get_patient_prompt(language=language)
        else:
            # Determine context type based on language
            if language == "pt":
                context_type = "do paciente" if is_professional_query else "seus"
            else:
                context_type = "patient" if is_professional_query else "your"
            base_instruction = template_loader.get_professional_prompt(context_type=context_type, language=language)
    except (FileNotFoundError, IOError) as e:
        logger.warning(f"Failed to load template, using fallback: {e}")
        # Fallback to hardcoded prompts if template loading fails
        if user_role == "patient":
            if language == "pt":
                base_instruction = (
                    "Você é um assistente médico com acesso aos seus registros médicos armazenados e resultados de análise de IA. "
                    "Forneça orientações personalizadas em termos claros com base em suas informações médicas documentadas. "
                    "Eu referencio análises de IA anteriores—não posso realizar novas análises de imagem. "
                    "Sempre recomende consultar profissionais de saúde para questões médicas."
                )
            else:
                base_instruction = (
                    "You are a medical assistant with access to your stored medical records and AI analysis results. "
                    "Provide personalized guidance in clear terms based on your documented medical information. "
                    "I reference previous AI analysis—I cannot perform new image analysis. "
                    "Always recommend consulting healthcare professionals for medical concerns."
                )
        else:
            if language == "pt":
                context_type = "do paciente" if is_professional_query else "seus"
                base_instruction = (
                    f"Você é um assistente médico para profissionais de saúde com acesso aos registros médicos {context_type}. "
                    f"Forneça insights clínicos baseados em resultados de análises armazenadas e achados documentados. "
                    f"Inclua achados médicos relevantes para tomada de decisão clínica."
                )
            else:
                context_type = "patient" if is_professional_query else "your"
                base_instruction = (
                    f"You are a medical assistant for healthcare professionals with access to {context_type} medical records. "
                    f"Provide clinical insights based on stored analysis results and documented findings. "
                    f"Include relevant medical findings for clinical decision-making."
                )

    # Generate medical overview and structured context
    if any(context_data.get(key) for key in ["documents", "medical_keywords", "medical_images", "pathological_findings"]):
        overview = _format_medical_overview(context_data)
        structured_context = _format_structured_medical_context(context_data)

        system_msg = f"{base_instruction}\n\n{overview}\n\n{structured_context}"

        # Add concise source attribution
        system_msg += "\n\n💡 Reference source documents and clarify you're using stored analysis, not performing new analysis."
    else:
        system_msg = base_instruction

    return [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": question},
    ]


def _format_medical_overview(context_data: Dict[str, Any]) -> str:
    """Generate a concise medical overview with statistics and categorized keywords."""
    overview_parts = []

    # Document statistics
    docs = context_data.get("documents", [])
    findings = context_data.get("pathological_findings", [])

    if docs:
        # Count by type
        image_count = sum(1 for doc in docs if doc.get("content_type") == "image")
        total_count = len(docs)

        stats = f"📋 Medical Records: {total_count} files"
        if image_count > 0:
            stats += f" ({image_count} images"
            if image_count < total_count:
                stats += f", {total_count - image_count} other"
            stats += ")"
        overview_parts.append(stats)

    # Findings summary
    if findings:
        pathological = [f for f in findings if not f.startswith("normal_")]
        normal = [f for f in findings if f.startswith("normal_")]

        summary = f"⚕️ Analysis: {len(pathological)} pathological findings"
        if normal:
            summary += f", {len(normal)} normal indicators"
        overview_parts.append(summary)

    # Categorized keywords
    keywords = context_data.get("medical_keywords", [])
    if keywords:
        categorized = _categorize_medical_keywords(keywords)
        if categorized:
            overview_parts.append(f"🔬 Keywords: {categorized}")

    return "\n".join(overview_parts)


def _categorize_medical_keywords(keywords: List[str]) -> str:
    """Categorize and summarize medical keywords to reduce redundancy."""
    categories = {
        "Dermatology": ["dermatology", "skin", "pigmentation", "lesion", "dermatological"],
        "Imaging": ["imaging", "resolution", "clinical documentation", "medical imaging"],
        "Monitoring": ["monitoring", "follow-up", "routine", "preventive"],
        "Assessment": ["condition", "finding", "assessment", "analysis"]
    }

    categorized_counts = {}
    uncategorized = []

    for keyword in keywords:
        categorized = False
        for category, terms in categories.items():
            if any(term in keyword.lower() for term in terms):
                categorized_counts[category] = categorized_counts.get(category, 0) + 1
                categorized = True
                break
        if not categorized:
            uncategorized.append(keyword)

    # Build summary
    summary_parts = []
    for category, count in categorized_counts.items():
        summary_parts.append(f"{category} ({count})")

    # Add top uncategorized terms (limit to 3)
    if uncategorized:
        top_uncategorized = uncategorized[:3]
        summary_parts.append(f"Other: {', '.join(top_uncategorized)}")

    return ", ".join(summary_parts)


def _format_structured_medical_context(context_data: Dict[str, Any]) -> str:
    """Format medical context in a structured, hierarchical format."""
    sections = []

    # Medical images section (grouped by type)
    images = context_data.get("medical_images", [])
    if images:
        sections.append(_format_grouped_medical_images(images))

    # Pathological findings section (categorized with sources)
    findings = context_data.get("pathological_findings", [])
    if findings:
        sections.append(_format_categorized_findings(findings, images))

    return "\n\n".join(sections)


def _format_grouped_medical_images(images: List[Dict[str, Any]]) -> str:
    """Format medical images grouped by type for better organization."""
    # Group images by medical type
    grouped = {}
    for img in images:
        metadata = img.get('metadata', {})
        medical_type = metadata.get('medical_type', 'unknown')

        if medical_type not in grouped:
            grouped[medical_type] = []
        grouped[medical_type].append(img)

    sections = []
    type_icons = {
        'dermatological_image': '🔬',
        'radiological_scan': '📡',
        'medical_radiograph': '🩻',
        'unknown': '📄'
    }

    for img_type, type_images in grouped.items():
        icon = type_icons.get(img_type, '📄')
        type_name = img_type.replace('_', ' ').title()

        section_header = f"{icon} {type_name} ({len(type_images)} files):"
        image_details = []

        for img in type_images:
            details = _format_compact_image_details(img)
            image_details.append(f"  • {details}")

        sections.append(f"{section_header}\n" + "\n".join(image_details))

    return "\n\n".join(sections)

def _format_compact_image_details(img: Dict[str, Any]) -> str:
    """Format individual image details in a compact format."""
    source = img.get('source', 'Unknown')
    metadata = img.get('metadata', {})

    # Basic info
    details = [source]

    # Dimensions (compact format)
    image_info = metadata.get('image_info', {})
    if image_info:
        width = image_info.get('width', 0)
        height = image_info.get('height', 0)
        if width and height:
            details.append(f"{width}x{height}")

    # Medical context analysis using shared utilities
    medical_context = extract_medical_context(metadata)
    if medical_context:
        # Relevance score
        relevance = medical_context.get('medical_relevance_score', 0)
        if relevance:
            details.append(f"Relevance: {relevance:.1f}")

        # Pathological analysis
        pathological_analysis = medical_context.get('pathological_analysis', {})
        if pathological_analysis and isinstance(pathological_analysis, dict):
            clinical_significance = pathological_analysis.get('clinical_significance', '')
            specific_findings, _ = get_pathological_findings(medical_context)

            if clinical_significance:
                details.append(f"Assessment: {clinical_significance}")

            if specific_findings:
                findings_str = ", ".join(specific_findings[:3])  # Limit to first 3
                if len(specific_findings) > 3:
                    findings_str += f" (+{len(specific_findings) - 3} more)"
                details.append(f"Findings: {findings_str}")

    return " | ".join(details)


def _format_categorized_findings(findings: List[str], images: List[Dict[str, Any]]) -> str:
    """Format pathological findings categorized by type with source attribution."""
    if not findings:
        return ""

    # Separate pathological from normal findings
    pathological = [f for f in findings if not f.startswith("normal_")]
    normal = [f for f in findings if f.startswith("normal_")]

    sections = []

    # Pathological findings
    if pathological:
        sections.append("⚠️ Pathological Findings:")
        for finding in pathological:
            # Add source attribution by checking which images contain this finding
            sources = _find_finding_sources(finding, images)
            source_text = f" ({', '.join(sources)})" if sources else ""
            sections.append(f"  • {finding.replace('_', ' ').title()}{source_text}")

    # Normal indicators
    if normal:
        sections.append("✅ Normal Indicators:")
        for finding in normal:
            clean_finding = finding.replace("normal_", "").replace("_", " ").title()
            sources = _find_finding_sources(finding, images)
            source_text = f" ({', '.join(sources)})" if sources else ""
            sections.append(f"  • {clean_finding}{source_text}")

    return "\n".join(sections)


def _find_finding_sources(finding: str, images: List[Dict[str, Any]]) -> List[str]:
    """Find which source documents contain a specific finding."""
    sources = []

    for img in images:
        try:
            metadata = img.get('metadata', {})
            medical_context = extract_medical_context(metadata)

            if medical_context:
                specific_findings, normal_indicators = get_pathological_findings(medical_context)

                # Check if finding exists in this image
                clean_finding = finding.replace("normal_", "")
                if (finding in specific_findings or
                    clean_finding in specific_findings or
                    clean_finding in normal_indicators):
                    source = img.get('source', 'Unknown')
                    if source not in sources:
                        sources.append(source)
        except Exception as e:
            logger.warning(f"Error checking findings for image {img.get('source', 'Unknown')}: {e}")
            continue

    return sources
