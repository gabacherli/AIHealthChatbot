"""
Document sharing API routes.
This module contains the REST API endpoints for document sharing between patients and professionals.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from ...services.document_sharing_service import DocumentSharingService
from ...services.audit_service import AuditService
from ...models.database import User

# Create blueprint
sharing_bp = Blueprint("document_sharing", __name__)

# Initialize services
document_sharing_service = DocumentSharingService()
audit_service = AuditService()


def get_current_user():
    """Get the current user from JWT token."""
    claims = get_jwt()
    username = claims.get("sub")  # JWT contains username, not user_id
    if username:
        return User.query.filter_by(username=username).first()
    return None


@sharing_bp.route("/patients/<int:patient_id>/shared", methods=["GET"])
@jwt_required()
def get_patient_shared_documents(patient_id):
    """
    Get all documents for a patient with sharing status.
    Only accessible by the patient themselves or their assigned professionals.
    """
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({"error": "User not found"}), 401

        # Check access permissions
        if current_user.role == 'patient':
            # Patients can only access their own documents
            if current_user.id != patient_id:
                return jsonify({"error": "Access denied"}), 403
        elif current_user.role == 'professional':
            # Professionals can only access documents of their assigned patients
            has_access = document_sharing_service.relationship_service.check_access_permission(
                patient_id=patient_id,
                professional_id=current_user.id,
                permission_type='can_view_documents'
            )
            if not has_access:
                return jsonify({"error": "Access denied"}), 403
        else:
            return jsonify({"error": "Invalid user role"}), 403

        # Get documents with sharing information
        documents = document_sharing_service.get_patient_shared_documents(patient_id)

        # Log the access
        audit_service.log_action(
            action='patient_documents_accessed',
            resource_type='document',
            user_id=current_user.id,
            details={
                'patient_id': patient_id,
                'document_count': len(documents),
                'access_type': 'shared_documents_list'
            }
        )

        return jsonify({
            "patient_id": patient_id,
            "documents": documents,
            "total_count": len(documents)
        }), 200

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@sharing_bp.route("/professionals/<int:professional_id>/patient-documents", methods=["GET", "OPTIONS"])
def get_professional_patient_documents(professional_id):
    """
    Get all patient documents accessible to a healthcare professional.
    Only accessible by the professional themselves.
    """
    # Handle CORS preflight request
    if request.method == 'OPTIONS':
        from flask import make_response
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization")
        response.headers.add('Access-Control-Allow-Methods', "GET,OPTIONS")
        return response

    # Apply JWT requirement only for non-OPTIONS requests
    from flask_jwt_extended import verify_jwt_in_request
    verify_jwt_in_request()

    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({"error": "User not found"}), 401

        # Only allow the professional themselves to access this endpoint
        if current_user.role != 'professional' or current_user.id != professional_id:
            return jsonify({"error": "Access denied"}), 403

        # Get optional patient filter
        patient_id = request.args.get('patient_id', type=int)

        # Get shared documents
        documents = document_sharing_service.get_shared_documents_for_professional(
            professional_id=professional_id,
            patient_id=patient_id
        )

        # Group documents by patient for better organization
        documents_by_patient = {}
        for doc in documents:
            pid = doc['patient_id']
            if pid not in documents_by_patient:
                documents_by_patient[pid] = {
                    'patient_id': pid,
                    'patient_name': doc['patient_name'],
                    'patient_username': doc['patient_username'],
                    'documents': []
                }
            documents_by_patient[pid]['documents'].append(doc)

        return jsonify({
            "professional_id": professional_id,
            "documents_by_patient": list(documents_by_patient.values()),
            "total_documents": len(documents),
            "total_patients": len(documents_by_patient)
        }), 200

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@sharing_bp.route("/access-check/<document_id>", methods=["GET"])
@jwt_required()
def check_document_access(document_id):
    """
    Check if the current user has access to a specific document.
    """
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({"error": "User not found"}), 401

        # Check access permissions
        permissions = document_sharing_service.check_document_access(
            user_id=current_user.id,
            document_id=document_id,
            user_role=current_user.role
        )

        return jsonify({
            "document_id": document_id,
            "user_id": current_user.id,
            "permissions": permissions,
            "has_access": permissions.get('can_view', False)
        }), 200

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@sharing_bp.route("/audit/<document_id>", methods=["GET"])
@jwt_required()
def get_document_audit_logs(document_id):
    """
    Get audit logs for a specific document.
    Only accessible by the document owner or assigned professionals.
    """
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({"error": "User not found"}), 401

        # Check if user has access to view audit logs for this document
        permissions = document_sharing_service.check_document_access(
            user_id=current_user.id,
            document_id=document_id,
            user_role=current_user.role
        )

        if not permissions.get('can_view', False):
            return jsonify({"error": "Access denied"}), 403

        # Get number of days from query parameter
        days = request.args.get('days', default=30, type=int)
        if days > 365:  # Limit to 1 year
            days = 365

        # Get audit logs
        logs = document_sharing_service.get_document_access_logs(document_id, days)

        # Log this audit access
        audit_service.log_action(
            action='audit_logs_accessed',
            resource_type='document',
            user_id=current_user.id,
            resource_id=document_id,
            details={'days_requested': days, 'logs_count': len(logs)}
        )

        return jsonify({
            "document_id": document_id,
            "audit_logs": logs,
            "period_days": days,
            "total_entries": len(logs)
        }), 200

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@sharing_bp.route("/patients/<int:patient_id>/access-summary", methods=["GET"])
@jwt_required()
def get_patient_access_summary(patient_id):
    """
    Get a summary of who has accessed a patient's data.
    Only accessible by the patient themselves or their assigned professionals.
    """
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({"error": "User not found"}), 401

        # Check access permissions
        if current_user.role == 'patient':
            # Patients can only access their own summary
            if current_user.id != patient_id:
                return jsonify({"error": "Access denied"}), 403
        elif current_user.role == 'professional':
            # Professionals can only access summaries of their assigned patients
            has_access = document_sharing_service.relationship_service.check_access_permission(
                patient_id=patient_id,
                professional_id=current_user.id,
                permission_type='can_view_documents'
            )
            if not has_access:
                return jsonify({"error": "Access denied"}), 403
        else:
            return jsonify({"error": "Invalid user role"}), 403

        # Get number of days from query parameter
        days = request.args.get('days', default=30, type=int)
        if days > 365:  # Limit to 1 year
            days = 365

        # Get access summary
        summary = document_sharing_service.get_patient_access_summary(patient_id, days)

        # Log this access
        audit_service.log_action(
            action='access_summary_viewed',
            resource_type='user',
            user_id=current_user.id,
            resource_id=str(patient_id),
            details={'days_requested': days, 'viewer_role': current_user.role}
        )

        return jsonify(summary), 200

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@sharing_bp.route("/log-access", methods=["POST"])
@jwt_required()
def log_document_access():
    """
    Manually log document access (for frontend tracking).

    Expected JSON:
    {
        "document_id": str,
        "access_type": str,
        "success": bool (optional, default: true)
    }
    """
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({"error": "User not found"}), 401

        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        document_id = data.get('document_id')
        access_type = data.get('access_type')
        success = data.get('success', True)

        if not document_id or not access_type:
            return jsonify({"error": "document_id and access_type are required"}), 400

        # Verify user has access to this document
        permissions = document_sharing_service.check_document_access(
            user_id=current_user.id,
            document_id=document_id,
            user_role=current_user.role
        )

        if not permissions.get('can_view', False):
            return jsonify({"error": "Access denied"}), 403

        # Log the access
        document_sharing_service.log_document_access(
            user_id=current_user.id,
            document_id=document_id,
            access_type=access_type,
            success=success
        )

        return jsonify({"message": "Access logged successfully"}), 200

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500
