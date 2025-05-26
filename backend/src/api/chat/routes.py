"""
Chat routes.
This module contains the routes for chat functionality.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from ...services.chat_service import get_answer_with_context
from ...services.audit_service import audit_service
import logging

logger = logging.getLogger(__name__)

chat_bp = Blueprint("chat", __name__, url_prefix="/chat")

@chat_bp.route("", methods=["POST"])
@jwt_required()
def chat():
    """
    Enhanced chat route with document retrieval and prompt enrichment.

    Expected JSON:
    {
        "question": str,
        "patient_id": int (optional, for healthcare professionals)
    }

    Returns:
        A JSON response with the answer, sources, and metadata.
    """
    claims = get_jwt()
    role = claims.get("role", "patient")
    user_id = claims.get("user_id", claims.get("sub", "anonymous"))  # Use user_id first, fallback to sub

    # Ensure user_id is a string for consistency
    if isinstance(user_id, int):
        user_id = str(user_id)

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    question = data.get("question", "")
    patient_id = data.get("patient_id")

    if not question:
        return jsonify({"error": "No question provided"}), 400

    try:
        # Validate patient_id for professionals
        if role == "professional" and patient_id:
            try:
                patient_id = int(patient_id)
            except (ValueError, TypeError):
                return jsonify({"error": "Invalid patient_id format"}), 400

        # Log the chat request
        audit_service.log_user_action(
            user_id=user_id,
            action='chat_request',
            details={
                'question_length': len(question),
                'role': role,
                'patient_id': patient_id if role == "professional" else None,
                'has_patient_context': bool(role == "professional" and patient_id)
            }
        )

        # Get answer with enhanced context and sources
        result = get_answer_with_context(
            question=question,
            role=role,
            user_id=user_id,
            patient_id=str(patient_id) if patient_id else None,
            language="pt"  # Default to Portuguese as per user preferences
        )

        # Check if result is a tuple (answer, sources)
        if isinstance(result, tuple) and len(result) == 2:
            answer, sources = result

            # Log successful response
            audit_service.log_user_action(
                user_id=user_id,
                action='chat_response_generated',
                details={
                    'sources_count': len(sources),
                    'answer_length': len(answer),
                    'role': role,
                    'patient_id': patient_id if role == "professional" else None
                }
            )

            response_data = {
                "answer": answer,
                "sources": sources,
                "metadata": {
                    "role": role,
                    "sources_count": len(sources),
                    "has_medical_context": len(sources) > 0,
                    "patient_context": bool(role == "professional" and patient_id)
                }
            }

            return jsonify(response_data)
        else:
            # Backward compatibility
            return jsonify({
                "answer": result,
                "sources": [],
                "metadata": {
                    "role": role,
                    "sources_count": 0,
                    "has_medical_context": False,
                    "patient_context": False
                }
            })

    except Exception as e:
        logger.error(f"Chat error for user {user_id}: {str(e)}")

        # Log the error
        audit_service.log_user_action(
            user_id=user_id,
            action='chat_error',
            details={
                'error': str(e),
                'role': role,
                'patient_id': patient_id if role == "professional" else None
            }
        )

        return jsonify({"error": "An error occurred while processing your request"}), 500


@chat_bp.route("/patients", methods=["GET"])
@jwt_required()
def get_available_patients():
    """
    Get list of patients available for healthcare professionals to query.
    Only accessible by healthcare professionals.

    Returns:
        A JSON response with the list of accessible patients.
    """
    claims = get_jwt()
    role = claims.get("role", "patient")
    user_id = claims.get("sub", "anonymous")

    if role != "professional":
        return jsonify({"error": "Access denied. Only healthcare professionals can access this endpoint."}), 403

    try:
        from ...services.relationship_service import RelationshipService
        relationship_service = RelationshipService()

        # Get professional's patients with active relationships
        patients = relationship_service.get_professional_patients(
            professional_id=int(user_id),
            status_filter='active'
        )

        # Format patient data for chat context
        formatted_patients = []
        for relationship in patients.get('relationships', []):
            patient = relationship.get('patient', {})
            formatted_patients.append({
                "id": patient.get('id'),
                "username": patient.get('username'),
                "full_name": patient.get('full_name'),
                "relationship_type": relationship.get('relationship_type'),
                "can_view_documents": relationship.get('can_view_documents', False)
            })

        # Log the access
        audit_service.log_user_action(
            user_id=user_id,
            action='chat_patients_list_accessed',
            details={
                'patients_count': len(formatted_patients),
                'role': role
            }
        )

        return jsonify({
            "patients": formatted_patients,
            "total_count": len(formatted_patients)
        })

    except Exception as e:
        logger.error(f"Error getting patients for professional {user_id}: {str(e)}")
        return jsonify({"error": "Failed to retrieve patient list"}), 500
