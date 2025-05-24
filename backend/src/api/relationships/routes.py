"""
Relationship management API routes.
This module contains the REST API endpoints for managing patient-professional relationships.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from ...services.relationship_service import RelationshipService
from ...services.audit_service import AuditService
from ...models.database import User
from . import relationships_bp

# Initialize services
relationship_service = RelationshipService()
audit_service = AuditService()


@relationships_bp.route("/test", methods=["GET"])
def test_endpoint():
    """Test endpoint to verify the relationships API is working."""
    return jsonify({"message": "Relationships API is working!", "status": "ok"})


def get_current_user():
    """Get the current user from JWT token."""
    claims = get_jwt()
    username = claims.get("sub")  # JWT contains username, not user_id
    if username:
        return User.query.filter_by(username=username).first()
    return None


def require_role(allowed_roles):
    """Decorator to require specific user roles."""
    def decorator(f):
        def wrapper(*args, **kwargs):
            user = get_current_user()
            if not user or user.role not in allowed_roles:
                return jsonify({"error": "Insufficient permissions"}), 403
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator


@relationships_bp.route("/", methods=["POST"])
@jwt_required()
@require_role(['professional', 'admin'])
def create_relationship():
    """
    Create a new patient-professional relationship.

    Expected JSON:
    {
        "patient_id": int,
        "professional_id": int,
        "relationship_type": str (optional),
        "relationship_status": str (optional),
        "notes": str (optional),
        "permissions": dict (optional)
    }
    """
    try:
        data = request.get_json()
        current_user = get_current_user()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Validate required fields
        patient_id = data.get('patient_id')
        professional_id = data.get('professional_id')

        if not patient_id or not professional_id:
            return jsonify({"error": "patient_id and professional_id are required"}), 400

        # Only allow professionals to create relationships with themselves or admins
        if current_user.role == 'professional' and current_user.id != professional_id:
            return jsonify({"error": "Professionals can only create relationships for themselves"}), 403

        success, message, relationship = relationship_service.create_relationship(
            patient_id=patient_id,
            professional_id=professional_id,
            relationship_type=data.get('relationship_type', 'primary_care'),
            relationship_status=data.get('relationship_status', 'active'),
            created_by_id=current_user.id,
            notes=data.get('notes'),
            permissions=data.get('permissions')
        )

        if success:
            return jsonify({
                "message": message,
                "relationship": relationship.to_dict(include_users=True)
            }), 201
        else:
            return jsonify({"error": message}), 400

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@relationships_bp.route("/<int:relationship_id>", methods=["GET"])
@jwt_required()
def get_relationship(relationship_id):
    """Get a specific relationship by ID."""
    try:
        current_user = get_current_user()
        relationship = relationship_service.get_relationship_by_id(relationship_id)

        if not relationship:
            return jsonify({"error": "Relationship not found"}), 404

        # Check if user has permission to view this relationship
        if (current_user.role == 'patient' and current_user.id != relationship['patient_id']) or \
           (current_user.role == 'professional' and current_user.id != relationship['professional_id']):
            return jsonify({"error": "Access denied"}), 403

        # Log the access
        audit_service.log_relationship_access(
            user_id=current_user.id,
            relationship_id=relationship_id,
            action='viewed',
            patient_id=relationship['patient_id'],
            professional_id=relationship['professional_id']
        )

        return jsonify({"relationship": relationship}), 200

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@relationships_bp.route("/<int:relationship_id>", methods=["PUT"])
@jwt_required()
@require_role(['professional', 'admin'])
def update_relationship(relationship_id):
    """
    Update an existing relationship.

    Expected JSON:
    {
        "relationship_status": str (optional),
        "relationship_type": str (optional),
        "notes": str (optional),
        "permissions": dict (optional)
    }
    """
    try:
        data = request.get_json()
        current_user = get_current_user()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Get the relationship to check permissions
        relationship = relationship_service.get_relationship_by_id(relationship_id)
        if not relationship:
            return jsonify({"error": "Relationship not found"}), 404

        # Only allow the professional in the relationship or admin to update
        if current_user.role == 'professional' and current_user.id != relationship['professional_id']:
            return jsonify({"error": "Access denied"}), 403

        # Prepare update data
        update_data = {}
        allowed_fields = ['relationship_status', 'relationship_type', 'notes']

        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]

        # Handle permissions
        if 'permissions' in data:
            permissions = data['permissions']
            if 'can_view_documents' in permissions:
                update_data['can_view_documents'] = permissions['can_view_documents']
            if 'can_add_notes' in permissions:
                update_data['can_add_notes'] = permissions['can_add_notes']
            if 'can_request_tests' in permissions:
                update_data['can_request_tests'] = permissions['can_request_tests']

        success, message, updated_relationship = relationship_service.update_relationship(
            relationship_id=relationship_id,
            updated_by_id=current_user.id,
            **update_data
        )

        if success:
            return jsonify({
                "message": message,
                "relationship": updated_relationship.to_dict(include_users=True)
            }), 200
        else:
            return jsonify({"error": message}), 400

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@relationships_bp.route("/<int:relationship_id>", methods=["DELETE"])
@jwt_required()
@require_role(['professional', 'admin'])
def delete_relationship(relationship_id):
    """
    Terminate a relationship.

    Expected JSON (optional):
    {
        "reason": str
    }
    """
    try:
        data = request.get_json() or {}
        current_user = get_current_user()

        # Get the relationship to check permissions
        relationship = relationship_service.get_relationship_by_id(relationship_id)
        if not relationship:
            return jsonify({"error": "Relationship not found"}), 404

        # Only allow the professional in the relationship or admin to delete
        if current_user.role == 'professional' and current_user.id != relationship['professional_id']:
            return jsonify({"error": "Access denied"}), 403

        success, message = relationship_service.delete_relationship(
            relationship_id=relationship_id,
            deleted_by_id=current_user.id,
            reason=data.get('reason')
        )

        if success:
            return jsonify({"message": message}), 200
        else:
            return jsonify({"error": message}), 400

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@relationships_bp.route("/professionals/<int:professional_id>/patients", methods=["GET"])
@jwt_required()
def get_professional_patients(professional_id):
    """Get all patients for a healthcare professional."""
    try:
        current_user = get_current_user()

        # Only allow the professional themselves or admin to view their patients
        if current_user.role == 'professional' and current_user.id != professional_id:
            return jsonify({"error": "Access denied"}), 403

        status = request.args.get('status', 'active')
        relationships = relationship_service.get_professional_patients(professional_id, status)

        # Log the access
        audit_service.log_action(
            action='patients_list_accessed',
            resource_type='relationship',
            user_id=current_user.id,
            details={'professional_id': professional_id, 'status_filter': status}
        )

        return jsonify({"relationships": relationships}), 200

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@relationships_bp.route("/patients/<int:patient_id>/professionals", methods=["GET"])
@jwt_required()
def get_patient_professionals(patient_id):
    """Get all healthcare professionals for a patient."""
    try:
        current_user = get_current_user()

        # Only allow the patient themselves, their professionals, or admin to view
        if current_user.role == 'patient' and current_user.id != patient_id:
            return jsonify({"error": "Access denied"}), 403

        # If professional, check if they have a relationship with this patient
        if current_user.role == 'professional':
            has_access = relationship_service.check_access_permission(
                patient_id=patient_id,
                professional_id=current_user.id
            )
            if not has_access:
                return jsonify({"error": "Access denied"}), 403

        status = request.args.get('status', 'active')
        relationships = relationship_service.get_patient_professionals(patient_id, status)

        # Log the access
        audit_service.log_action(
            action='professionals_list_accessed',
            resource_type='relationship',
            user_id=current_user.id,
            details={'patient_id': patient_id, 'status_filter': status}
        )

        return jsonify({"relationships": relationships}), 200

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@relationships_bp.route("/search/professionals", methods=["GET"])
@jwt_required()
@require_role(['patient', 'professional', 'admin'])
def search_professionals():
    """Search for healthcare professionals."""
    try:
        query = request.args.get('q', '')
        specialty = request.args.get('specialty')
        organization = request.args.get('organization')

        professionals = relationship_service.search_professionals(
            query=query,
            specialty=specialty,
            organization=organization
        )

        return jsonify({"professionals": professionals}), 200

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500
