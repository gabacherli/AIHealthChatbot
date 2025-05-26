"""
Chat service.
This module contains the chat service functions.
"""
from .prompt_builder import build_prompt
from .document_service import document_service
from .relationship_service import RelationshipService
from openai import OpenAI
from ..config import get_config
import logging

logger = logging.getLogger(__name__)

config = get_config()

client = OpenAI(
    api_key=config.OPENAI_API_KEY
)

relationship_service = RelationshipService()

def get_answer_with_context(question: str, role: str, user_id: str = None, patient_id: str = None) -> tuple:
    """
    Get an answer to a question with context from relevant medical documents.

    Args:
        question: The question to answer.
        role: The role of the user (patient or professional).
        user_id: The ID of the user asking the question.
        patient_id: The ID of the patient (for professionals accessing patient data).

    Returns:
        A tuple containing the answer and a list of sources.
    """


    try:
        # Determine which user's documents to search
        target_user_id = user_id

        if role == "professional" and patient_id:
            # Healthcare professional accessing patient documents
            # Verify access permission
            has_access = relationship_service.check_access_permission(
                patient_id=int(patient_id),
                professional_id=int(user_id),
                permission_type='can_view_documents'
            )

            if not has_access:
                logger.warning(f"Professional {user_id} denied access to patient {patient_id} documents")
                # Return response without patient context
                target_user_id = user_id
            else:
                logger.info(f"Professional {user_id} accessing patient {patient_id} documents for chat")
                target_user_id = patient_id

        # Retrieve context documents with enhanced filtering
        search_results = _retrieve_enhanced_context(
            question=question,
            user_id=target_user_id,
            role=role,
            is_professional_query=(role == "professional" and patient_id is not None)
        )

        # Extract and format context with medical metadata
        context_data = _format_context_with_metadata(search_results)

        # Build the enhanced prompt
        prompt_messages = build_prompt(
            question=question,
            context_data=context_data,
            user_role=role,
            is_professional_query=(role == "professional" and patient_id is not None)
        )

        # Generate response
        response = client.chat.completions.create(
            model=config.MODEL_NAME,
            messages=prompt_messages,
            temperature=0.5
        )

        answer = response.choices[0].message.content

        # Format sources with enhanced metadata
        sources = _format_sources_with_metadata(search_results)

        logger.info(f"Generated response with {len(sources)} sources for {role} user {user_id}")
        return answer, sources

    except Exception as e:
        logger.error(f"Error in get_answer_with_context: {str(e)}")
        # Fallback to basic response without context
        prompt_messages = build_prompt(question, {}, role)

        response = client.chat.completions.create(
            model=config.MODEL_NAME,
            messages=prompt_messages,
            temperature=0.5
        )

        return response.choices[0].message.content, []


def _retrieve_enhanced_context(question: str, user_id: str, role: str, is_professional_query: bool = False) -> list:
    """
    Retrieve enhanced context with medical metadata and keywords.

    Args:
        question: The search query
        user_id: The target user ID for document retrieval
        role: The user role
        is_professional_query: Whether this is a professional querying patient data

    Returns:
        List of enhanced search results with medical metadata
    """
    # Ensure user_id is the correct type for filtering
    # Try both string and integer versions to handle type mismatches
    try:
        user_id_int = int(user_id)
    except (ValueError, TypeError):
        user_id_int = user_id

    filters = {
        "user_id": user_id_int  # Use integer version to match document metadata
    }

    # Increase limit for professional queries to get comprehensive context
    limit = 8 if is_professional_query else 5

    # Search for relevant documents
    search_results = document_service.search_documents(
        query=question,
        filters=filters
    )

    # Enhance results with medical keywords and metadata
    enhanced_results = []
    for result in search_results[:limit]:
        enhanced_result = result.copy()

        # Add medical keywords if available
        metadata = result.get("metadata", {})
        if "medical_keywords" in metadata:
            enhanced_result["medical_keywords"] = metadata["medical_keywords"]

        # Add medical image classification if available
        if metadata.get("has_image_data") and "medical_classification" in metadata:
            enhanced_result["medical_classification"] = metadata["medical_classification"]

        # Add pathological findings if available
        pathological_findings = []

        try:
            # Check direct pathological_findings field
            if "pathological_findings" in metadata:
                findings = metadata["pathological_findings"]
                if isinstance(findings, list):
                    pathological_findings.extend(findings)
                elif isinstance(findings, str):
                    pathological_findings.append(findings)

            # Check nested pathological analysis in medical_context
            medical_context = metadata.get("medical_context")

            # Handle case where medical_context is a boolean True (indicating presence but wrong structure)
            if medical_context is True:
                # Look for medical context in image_info instead
                image_info = metadata.get("image_info", {})
                if isinstance(image_info, dict):
                    medical_context_alt = image_info.get("medical_context", {})
                    if isinstance(medical_context_alt, dict):
                        medical_context = medical_context_alt

            if medical_context and isinstance(medical_context, dict):
                pathological_analysis = medical_context.get("pathological_analysis")

                if pathological_analysis and isinstance(pathological_analysis, dict):
                    specific_findings = pathological_analysis.get("specific_findings")

                    if specific_findings and isinstance(specific_findings, list):
                        pathological_findings.extend(specific_findings)

                    # Also check for other pathological data
                    normal_indicators = pathological_analysis.get("normal_indicators", [])
                    if normal_indicators and isinstance(normal_indicators, list):
                        # Add normal indicators with a prefix to distinguish them
                        normal_findings = [f"normal_{indicator}" for indicator in normal_indicators]
                        pathological_findings.extend(normal_findings)

            if pathological_findings:
                enhanced_result["pathological_findings"] = pathological_findings

        except Exception as e:
            logger.error(f"Error extracting pathological findings from document {metadata.get('source', 'Unknown')}: {e}")

        enhanced_results.append(enhanced_result)

    return enhanced_results


def _format_context_with_metadata(search_results: list) -> dict:
    """
    Format context data with medical metadata for prompt enrichment.

    Args:
        search_results: List of search results with metadata

    Returns:
        Formatted context data dictionary
    """
    context_data = {
        "documents": [],
        "medical_keywords": set(),
        "medical_images": [],
        "pathological_findings": []
    }

    for result in search_results:
        doc_info = {
            "content": result["content"],
            "source": result.get("metadata", {}).get("source", "Unknown"),
            "upload_date": result.get("metadata", {}).get("upload_date"),
            "content_type": result.get("metadata", {}).get("content_type")
        }

        # Add medical keywords
        if "medical_keywords" in result:
            keywords = result["medical_keywords"]
            if isinstance(keywords, list):
                context_data["medical_keywords"].update(keywords)
            elif isinstance(keywords, str):
                context_data["medical_keywords"].add(keywords)

        # Add medical image information
        if result.get("metadata", {}).get("has_image_data"):
            image_info = {
                "source": doc_info["source"],
                "classification": result.get("medical_classification", {}),
                "upload_date": doc_info["upload_date"],
                "metadata": result.get("metadata", {})  # Include full metadata for prompt builder
            }
            context_data["medical_images"].append(image_info)

        # Add pathological findings
        if "pathological_findings" in result:
            findings = result["pathological_findings"]
            if findings:
                findings_list = findings if isinstance(findings, list) else [findings]
                context_data["pathological_findings"].extend(findings_list)

        # Also check for pathological findings in metadata (backup extraction)
        metadata = result.get("metadata", {})
        if metadata and not context_data["pathological_findings"]:  # Only if no findings found yet
            medical_context = metadata.get("medical_context", {})
            if isinstance(medical_context, dict):
                pathological_analysis = medical_context.get("pathological_analysis", {})
                if isinstance(pathological_analysis, dict):
                    specific_findings = pathological_analysis.get("specific_findings", [])
                    if isinstance(specific_findings, list) and specific_findings:
                        context_data["pathological_findings"].extend(specific_findings)

        context_data["documents"].append(doc_info)

    # Convert set to list for JSON serialization
    context_data["medical_keywords"] = list(context_data["medical_keywords"])

    return context_data


def _format_sources_with_metadata(search_results: list) -> list:
    """
    Format sources with enhanced metadata for response attribution.

    Args:
        search_results: List of search results

    Returns:
        List of formatted source information
    """
    sources = []

    for result in search_results:
        metadata = result.get("metadata", {})

        source_info = {
            "source": metadata.get("source", "Unknown"),
            "content_type": metadata.get("content_type", "Unknown"),
            "upload_date": metadata.get("upload_date"),
            "score": result.get("score", 0.0)
        }

        # Add medical metadata if available
        if "medical_keywords" in result:
            source_info["medical_keywords"] = result["medical_keywords"]

        if metadata.get("has_image_data"):
            source_info["has_medical_image"] = True
            if "medical_classification" in result:
                source_info["medical_classification"] = result["medical_classification"]

        sources.append(source_info)

    return sources
